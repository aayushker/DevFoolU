import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  "/", 
  "/api/heartbeat(.*)", 
  "/api/stats(.*)",
  "/sign-in(.*)",
  "/sign-up(.*)"
]);

// Invert the logic - protect everything except public routes
const isProtectedRoute = createRouteMatcher([
  "/((?!/).*)" // Match everything except the routes defined in isPublicRoute
]);

// By default, no routes are protected, so we need to explicitly protect non-public routes
export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
