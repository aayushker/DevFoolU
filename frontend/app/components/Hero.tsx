import { Button, Link } from "@nextui-org/react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/app/components/ui/card";
import { 
  Upload, 
  Search, 
  FileText, 
  Clock, 
  Database, 
  ChevronRight, 
  Shield, 
  Zap,
  Code,
  Check,
  Layers,
  BarChart
} from "lucide-react";
import "react-toastify/dist/ReactToastify.css";
import React, { useState, useEffect } from "react";
import { Badge } from "@/app/components/ui/badge";
import { motion } from "framer-motion";

// Animation variants
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

const Hero = () => {
  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL;
  const [dbStats, setDbStats] = useState({
    total_projects: 0,
    processed_projects: 0,
    latest_projects: [],
    db_status: 'unavailable'
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkBackend = async () => {
      if (!backendURL) {
        console.error("Backend URL is undefined. Check your .env.local file.");
        toast.error("Backend URL configuration is missing.", {
          position: "bottom-right",
          toastId: "backend-config-error",
        });
        setIsLoading(false);
        return;
      }

      try {
        // Use the root URL for heartbeat endpoint
        const response = await axios.get(`${backendURL}`);
        console.log("Backend response:", response.data);
        
        if (response.status === 200) {
          toast.success("Backend is now active!", {
            position: "bottom-right",
            toastId: "backend-active",
          });
          
          // Fetch database stats
          try {
            const statsResponse = await axios.get(`${backendURL}/api/stats/`);
            if (statsResponse.status === 200 && statsResponse.data.status === 'success') {
              setDbStats(statsResponse.data.data);
            }
          } catch (statsError) {
            console.error("Error fetching database stats:", statsError);
          }
        }
      } catch (error) {
        console.error("Backend connection error:", error);
        toast.error("Unable to connect to backend.", {
          position: "bottom-right",
          toastId: "backend-error",
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    checkBackend();
  }, [backendURL]);
  
  return (
    <div>
      <ToastContainer />
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Detect Project Plagiarism with Confidence
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              Ensure the originality of Devfolio projects with our advanced
              AI-powered plagiarism detection system.
            </p>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                as={Link}
                href="/project"
                size="lg"
                className="bg-teal-500 hover:bg-teal-600 text-white text-lg px-8 py-6 rounded-lg shadow-lg"
              >
                Get Started Now <ChevronRight className="ml-2" />
              </Button>
            </motion.div>
          </motion.div>

          {/* Stats Cards */}
          <motion.div 
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16"
          >
            <motion.div variants={item}>
              <Card className="bg-white/10 backdrop-blur border-none text-white shadow-xl">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-2xl font-bold">Database Size</CardTitle>
                  <Database className="h-8 w-8 text-teal-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-5xl font-bold mb-2 text-teal-400">
                    {isLoading ? "..." : dbStats.total_projects.toLocaleString()}
                  </div>
                  <p className="text-blue-100">Indexed Projects</p>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div variants={item}>
              <Card className="bg-white/10 backdrop-blur border-none text-white shadow-xl">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-2xl font-bold">Processed</CardTitle>
                  <BarChart className="h-8 w-8 text-teal-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-5xl font-bold mb-2 text-teal-400">
                    {isLoading ? "..." : dbStats.processed_projects.toLocaleString()}
                  </div>
                  <p className="text-blue-100">Projects Analyzed</p>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div variants={item}>
              <Card className="bg-white/10 backdrop-blur border-none text-white shadow-xl">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-2xl font-bold">Speed</CardTitle>
                  <Zap className="h-8 w-8 text-teal-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-5xl font-bold mb-2 text-teal-400">
                    &lt;5s
                  </div>
                  <p className="text-blue-100">Average Check Time</p>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl font-bold text-blue-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our powerful plagiarism detection system works in three easy steps
            </p>
          </motion.div>

          <motion.div 
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {[
              { icon: Upload, text: "Upload Project URL", description: "Simply paste your Devfolio project URL and let us handle the rest" },
              { icon: Search, text: "AI Analysis", description: "Our advanced algorithms extract key information and analyze against our database" },
              { icon: FileText, text: "Get Results", description: "Receive detailed similarity analysis with potential matching projects" },
            ].map((step, index) => (
              <motion.div key={index} variants={item}>
                <Card className="h-full border-2 border-blue-100 hover:border-teal-500 transition-all duration-300 hover:shadow-xl">
                  <CardHeader>
                    <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
                      <step.icon className="w-8 h-8 text-blue-900" />
                    </div>
                    <CardTitle className="text-xl font-bold text-center text-blue-900">
                      {step.text}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 text-center">
                      {step.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl font-bold text-center mb-4 text-blue-900">
              Key Features
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Powered by advanced AI and a comprehensive database
            </p>
          </motion.div>
          
          <motion.div 
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {[
              {
                icon: Search,
                title: "99% Accuracy",
                description:
                  "State-of-the-art algorithms for precise plagiarism identification",
              },
              {
                icon: Clock,
                title: "Real-Time Results",
                description: "Get results in seconds, not minutes",
              },
              {
                icon: Shield,
                title: "Defend Your Work",
                description:
                  "Protect your original ideas and contributions",
              },
              {
                icon: Layers,
                title: "Massive Database",
                description:
                  `${dbStats.total_projects.toLocaleString()}+ projects indexed for comprehensive checks`,
              },
              {
                icon: Code,
                title: "Tech Stack Analysis",
                description:
                  "Understand tech similarities between projects",
              },
              {
                icon: Check,
                title: "Clear Reports",
                description:
                  "Easy-to-understand reports with actionable insights",
              },
            ].map((feature, index) => (
              <motion.div key={index} variants={item}>
                <Card className="h-full hover:shadow-xl transition-all duration-300">
                  <CardHeader className="pb-2">
                    <feature.icon className="w-10 h-10 text-teal-500 mb-2" />
                    <CardTitle className="text-xl text-blue-900">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-600">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Latest Projects Section */}
      {!isLoading && dbStats.latest_projects.length > 0 && (
        <section className="py-20 bg-gray-50">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl font-bold text-blue-900 mb-4">
                Latest Projects Added
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Some of the most recent projects in our database
              </p>
            </motion.div>
            
            <motion.div 
              variants={container}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {dbStats.latest_projects.map((project, index) => (
                <motion.div key={index} variants={item}>
                  <Card className="h-full hover:shadow-xl transition-all duration-300 border border-gray-200">
                    <CardHeader>
                      <CardTitle className="text-lg font-bold text-blue-900 line-clamp-1">
                        {project.project_name || "Unnamed Project"}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {project.tech_stack && project.tech_stack.split(', ').slice(0, 5).map((tech, techIndex) => (
                          <Badge key={techIndex} variant="outline" className="bg-blue-50">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => window.open(project.project_url, '_blank')}
                        className="w-full text-blue-900 border-blue-900 hover:bg-blue-900 hover:text-white"
                      >
                        View on Devfolio
                      </Button>
                    </CardFooter>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold mb-6">
              Ready to Safeguard Your Projects?
            </h2>
            <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
              Join thousands of developers who trust our platform to verify their project originality
            </p>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                as={Link}
                href="/project"
                size="lg"
                className="bg-teal-500 hover:bg-teal-600 text-white text-lg px-8 py-6 rounded-lg shadow-lg"
              >
                Check Your Project Now <ChevronRight className="ml-2" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Hero;
