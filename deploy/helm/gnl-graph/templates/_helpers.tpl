{{- /*
Helpers pour le chart GNL Graph
*/ -}}

{{- define "gnl-graph.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "gnl-graph.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "gnl-graph.labels" -}}
helm.sh/chart: {{ include "gnl-graph.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "gnl-graph.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "gnl-graph.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gnl-graph.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "gnl-graph.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "gnl-graph.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "gnl-graph.neo4j.url" -}}
{{- printf "bolt://%s-neo4j:7687" .Release.Name }}
{{- end }}

{{- define "gnl-graph.qdrant.url" -}}
{{- printf "http://%s-qdrant:6333" .Release.Name }}
{{- end }}

{{- define "gnl-graph.redis.url" -}}
{{- printf "redis://%s-redis:6379" .Release.Name }}
{{- end }}

{{- define "gnl-graph.kafka.url" -}}
{{- printf "%s-kafka:9092" .Release.Name }}
{{- end }}

{{- define "gnl-graph.imagePullSecret" -}}
{{- with .Values.imagePullSecrets }}
{{- toYaml . }}
{{- end }}
{{- end }}