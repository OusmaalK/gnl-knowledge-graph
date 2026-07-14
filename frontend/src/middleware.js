import { NextResponse } from 'next/server';

export function middleware(request) {
  // Récupérer le token depuis les cookies
  const token = request.cookies.get('token')?.value;
  const pathname = request.nextUrl.pathname;

  // Liste des pages publiques (accessibles sans connexion)
  const publicPaths = ['/auth/login', '/auth/register'];
  const isPublicPath = publicPaths.includes(pathname);

  // Si l'utilisateur n'est pas connecté ET essaie d'accéder à une page privée
  if (!token && !isPublicPath) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  // Si l'utilisateur est connecté ET essaie d'accéder à une page de login/register
  if (token && isPublicPath) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

// Configuration : Appliquer le middleware à TOUTES les routes sauf les assets statiques
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};