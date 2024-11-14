import { Button, Input, Link } from "@nextui-org/react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Upload, Search, FileText, Clock, Database } from "lucide-react";
import "react-toastify/dist/ReactToastify.css";
import React from "react";
import { useEffect } from "react";

const Hero = () => {
  const backendURL = process.env.NEXT_PUBLIC_URL;

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await axios.get(`${backendURL}`);
        if (response.status === 200) {
          toast.success("Backend is now active!", {
            position: "bottom-right",
            toastId: "backend-active",
          });
        }
      } catch (error) {
        toast.error("Unable to connect to backend.", {
          position: "bottom-right",
          toastId: "backend-error",
        });
      }
    };
    checkBackend();
  }, []);
  return (
    <div>
      <ToastContainer />
      {/* Hero Section */}
      <section className="bg-blue-900 text-white py-20">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Detect Project Plagiarism with Ease
          </h1>
          <p className="text-xl mb-12 max-w-2xl">
            Ensure the originality of Devfolio projects with our advanced
            plagiarism detection tool. Our fight against Plagiarism.
          </p>

          <div className="flex flex-wrap justify-center gap-8 mb-12">
            {[
              { icon: Upload, text: "Upload Project" },
              { icon: Search, text: "Automated Check" },
              { icon: FileText, text: "Report" },
            ].map((step, index) => (
              <Card key={index} className="w-64 bg-white text-blue-900">
                <CardHeader>
                  <step.icon className="w-12 h-12 mx-auto text-teal-500" />
                </CardHeader>
                <CardContent>
                  <h3 className="text-lg font-semibold text-center">
                    {step.text}
                  </h3>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-blue-900">
            Our Core Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                title: "Accurate Detection",
                description:
                  "State-of-the-art algorithms for precise plagiarism identification",
              },
              {
                icon: Clock,
                title: "Faster Detection",
                description: "Quick turnaround time for instant results",
              },
              {
                icon: Database,
                title: "Database of 186k Projects",
                description:
                  "Extensive repository for comprehensive comparisons",
              },
            ].map((feature, index) => (
              <Card key={index}>
                <CardHeader>
                  <feature.icon className="w-12 h-12 mx-auto text-teal-500" />
                  <CardTitle className="text-center">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-900 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">
            Ready to Safeguard Your Projects?
          </h2>
          <Button
            size="lg"
            className="bg-teal-500 hover:bg-teal-600 text-white"
          >
            <Link href="/project" className="text-inherit">
              Get Started{" "}
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Hero;
