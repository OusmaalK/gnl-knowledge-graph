"""
Entraînement et fine-tuning des modèles LLM
"""

import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import json
from .dataset import DatasetBuilder

logger = logging.getLogger(__name__)

class FineTuner:
    """
    Fine-tuning des modèles LLM avec LoRA
    """
    
    def __init__(self, model_name: str = "llama3:70b", output_dir: str = "models/fine_tuned"):
        """
        Initialise le fine-tuner
        
        Args:
            model_name: Nom du modèle de base
            output_dir: Dossier de sortie
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset_builder = DatasetBuilder()
        
        self.model = None
        self.tokenizer = None
        self.lora_config = None
        
        logger.info(f"🔧 FineTuner - Modèle: {model_name}")
    
    def setup_model(self, use_4bit: bool = True):
        """
        Configure le modèle pour le fine-tuning
        """
        try:
            # Charger le tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Charger le modèle
            kwargs = {}
            if use_4bit:
                kwargs['load_in_4bit'] = True
                kwargs['bnb_4bit_compute_dtype'] = torch.float16
                kwargs['bnb_4bit_quant_type'] = 'nf4'
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map='auto',
                torch_dtype=torch.float16,
                **kwargs
            )
            
            # Préparer pour l'entraînement LoRA
            self.model = prepare_model_for_kbit_training(self.model)
            
            # Configuration LoRA
            self.lora_config = LoraConfig(
                r=16,
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                task_type="CAUSAL_LM"
            )
            
            self.model = get_peft_model(self.model, self.lora_config)
            self.model.print_trainable_parameters()
            
            logger.info("✅ Modèle configuré pour le fine-tuning")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration : {e}")
            return False
    
    def prepare_dataset(self, dataset_path: Optional[str] = None) -> Tuple[Dataset, Dataset]:
        """
        Prépare le dataset pour l'entraînement
        """
        if dataset_path:
            data = self.dataset_builder.load_dataset(dataset_path)
        else:
            # Créer des données d'exemple
            sample_data = [
                {'instruction': 'Diagnostiquer un incident', 'output': 'Incident de corrosion détecté'},
                {'instruction': 'Analyser un pipeline', 'output': 'Pipeline en état critique'}
            ]
            data = sample_data
        
        # Formater les données
        formatted_data = []
        for item in data:
            text = f"Instruction: {item['instruction']}\nRéponse: {item['output']}"
            formatted_data.append(text)
        
        # Tokeniser
        train_texts, eval_texts = self._split_texts(formatted_data)
        
        train_dataset = self._create_dataset(train_texts)
        eval_dataset = self._create_dataset(eval_texts)
        
        return train_dataset, eval_dataset
    
    def _split_texts(self, texts: List[str], ratio: float = 0.8) -> Tuple[List[str], List[str]]:
        """Divise les textes en train/eval"""
        import random
        random.seed(42)
        random.shuffle(texts)
        split = int(len(texts) * ratio)
        return texts[:split], texts[split:]
    
    def _create_dataset(self, texts: List[str]):
        """Crée un dataset PyTorch"""
        class TextDataset(Dataset):
            def __init__(self, texts, tokenizer, max_length=512):
                self.texts = texts
                self.tokenizer = tokenizer
                self.max_length = max_length
            
            def __len__(self):
                return len(self.texts)
            
            def __getitem__(self, idx):
                text = self.texts[idx]
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                return {
                    'input_ids': encoding['input_ids'].squeeze(),
                    'attention_mask': encoding['attention_mask'].squeeze(),
                    'labels': encoding['input_ids'].squeeze()
                }
        
        return TextDataset(texts, self.tokenizer)
    
    def train(self, dataset_path: Optional[str] = None, epochs: int = 3, batch_size: int = 4):
        """
        Exécute le fine-tuning
        """
        if not self.model:
            if not self.setup_model():
                return False
        
        # Préparer le dataset
        train_dataset, eval_dataset = self.prepare_dataset(dataset_path)
        
        # Arguments d'entraînement
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=50,
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            push_to_hub=False,
            report_to="none",
            fp16=True
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )
        
        logger.info("🚀 Début de l'entraînement...")
        
        try:
            trainer.train()
            trainer.save_model(str(self.output_dir / "final_model"))
            logger.info(f"✅ Fine-tuning terminé - Modèle sauvegardé dans {self.output_dir}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur entraînement : {e}")
            return False
    
    def load_fine_tuned_model(self, model_path: Optional[str] = None):
        """
        Charge un modèle fine-tuné
        """
        path = model_path or str(self.output_dir / "final_model")
        if not os.path.exists(path):
            logger.error(f"❌ Modèle non trouvé : {path}")
            return None
        
        try:
            from peft import PeftModel
            model = PeftModel.from_pretrained(self.model, path)
            logger.info(f"✅ Modèle fine-tuné chargé : {path}")
            return model
        except Exception as e:
            logger.error(f"❌ Erreur chargement : {e}")
            return None

if __name__ == "__main__":
    # Test du fine-tuner
    tuner = FineTuner()
    print("✅ FineTuner prêt")