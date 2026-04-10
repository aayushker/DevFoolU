"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { projectsAPI, authAPI } from "@/lib/api";
import { Zap, Plus, Trash2, ExternalLink, FolderOpen, LogOut, Brain, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

interface User {
  id: number;
  username: string;
  email: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newProject, setNewProject] = useState({ name: "", description: "" });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) { router.push("/login"); return; }
      const [u, p] = await Promise.all([authAPI.getProfile(), projectsAPI.getAll()]);
      setUser(u.data);
      setProjects(p.data);
    } catch (err: any) {
      if (err.response?.status === 401) { localStorage.removeItem("token"); router.push("/login"); }
      else setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await projectsAPI.create(newProject);
      setNewProject({ name: "", description: "" });
      setShowForm(false);
      fetchAll();
    } catch { setError("Failed to create project"); }
    finally { setCreating(false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this project?")) return;
    try { await projectsAPI.delete(id.toString()); fetchAll(); }
    catch { setError("Failed to delete project"); }
  };

  const handleLogout = () => { localStorage.removeItem("token"); router.push("/login"); };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#050816]">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/30 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050816]">
      {/* Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-violet-700/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Sidebar-style header */}
      <header className="sticky top-0 z-50 border-b border-white/10 bg-[#050816]/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-purple-500 rounded-lg flex items-center justify-center">
                <Zap className="text-white" size={16} />
              </div>
              <span className="font-bold text-white">Dev<span className="text-purple-400">Fool</span>You</span>
            </Link>
            <nav className="hidden md:flex gap-5">
              <Link href="/dashboard" className="text-sm text-purple-400 font-semibold border-b border-purple-400 pb-0.5">
                Projects
              </Link>
              <Link href="/similarity" className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1.5">
                <Brain size={14} />
                AI Similarity
              </Link>
              <Link href="/check" className="text-sm text-gray-400 hover:text-white transition-colors">
                Check Project
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-400 hidden sm:block">Welcome, <span className="text-white font-semibold">{user?.username}</span></span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-red-400 border border-white/10 hover:border-red-500/30 px-3 py-1.5 rounded-lg transition-all"
            >
              <LogOut size={14} />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        {error && (
          <div className="mb-6 flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Header row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-white">Your Projects</h1>
            <p className="text-gray-400 text-sm mt-1">{projects.length} project{projects.length !== 1 ? "s" : ""} total</p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/check"
              className="flex items-center gap-2 text-sm border border-purple-500/30 text-purple-300 hover:bg-purple-500/10 px-4 py-2.5 rounded-xl transition-all"
            >
              Check Project
            </Link>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 text-sm bg-gradient-to-r from-violet-600 to-purple-500 text-white px-4 py-2.5 rounded-xl font-semibold hover:shadow-lg hover:shadow-purple-500/30 transition-all"
            >
              {showForm ? <X size={16} /> : <Plus size={16} />}
              {showForm ? "Cancel" : "New Project"}
            </button>
          </div>
        </div>

        {/* New project form */}
        <AnimatePresence>
          {showForm && (
            <motion.div
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
              className="mb-8 rounded-2xl border border-purple-500/30 bg-purple-500/5 p-6"
            >
              <h3 className="text-lg font-bold text-white mb-5">Create New Project</h3>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Project Name</label>
                  <input
                    type="text" required
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/15 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white placeholder-gray-600 text-sm"
                    placeholder="My Awesome Project"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Description</label>
                  <textarea
                    rows={3}
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/15 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white placeholder-gray-600 text-sm resize-none"
                    placeholder="Brief project description..."
                  />
                </div>
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-gradient-to-r from-violet-600 to-purple-500 text-white px-6 py-2.5 rounded-xl font-semibold text-sm hover:shadow-lg hover:shadow-purple-500/30 transition-all disabled:opacity-60"
                >
                  {creating ? "Creating..." : "Create Project"}
                </button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Projects grid */}
        {projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 rounded-2xl border border-dashed border-white/15">
            <FolderOpen size={48} className="text-gray-600 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No projects yet</h3>
            <p className="text-gray-500 mb-6">Create your first project to get started</p>
            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm"
            >
              <Plus size={16} /> Create Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {projects.map((project, i) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 hover:border-purple-500/40 hover:bg-white/[0.06] transition-all duration-300"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-white font-bold text-lg group-hover:text-purple-200 transition-colors line-clamp-1">
                    {project.name}
                  </h3>
                  <button
                    onClick={() => handleDelete(project.id)}
                    className="text-gray-600 hover:text-red-400 transition-colors flex-shrink-0 ml-2"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <p className="text-gray-500 text-sm mb-4 line-clamp-2 min-h-[2.5rem]">
                  {project.description || "No description provided"}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">
                    {new Date(project.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                  </span>
                  <Link
                    href={`/projects/${project.id}`}
                    className="inline-flex items-center gap-1.5 text-xs text-purple-400 hover:text-purple-300 font-semibold transition-colors group/link"
                  >
                    View Tasks
                    <ExternalLink size={12} className="group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
