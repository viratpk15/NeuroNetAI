import { redirect } from "next/navigation";

export default function HomePage() {
  // Redirect root to projects page
  redirect("/projects");
}
