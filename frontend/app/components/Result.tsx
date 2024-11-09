import React from "react";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/app/components/ui/alert";
import { Badge } from "@/app/components/ui/badge";
import { AlertTriangle } from "lucide-react";

const matchedProjects = [
  {
    title: "AI-Powered Smart Home Assistant",
    description:
      "Voice-controlled home automation system using machine learning",
    similarity: 85,
    techStack: ["React", "Node.js", "TensorFlow"],
  },
  {
    title: "Blockchain-based Supply Chain",
    description: "Decentralized tracking system for product authenticity",
    similarity: 62,
    techStack: ["Solidity", "Ethereum", "Web3.js"],
  },
  {
    title: "AR Navigation App",
    description: "Augmented reality app for indoor navigation",
    similarity: 45,
    techStack: ["Unity", "ARKit", "C#"],
  },
];

const Result = () => {
  return (
    <div className="flex-grow container mx-auto px-4 py-8">
      <Alert variant="destructive" className="mb-8">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>High Similarity Detected</AlertTitle>
        <AlertDescription>
          85% similarity detected with an existing project!
        </AlertDescription>
      </Alert>

      <h2 className="text-2xl font-bold mb-6 text-blue-900">
        Matched Projects
      </h2>

      <div className="space-y-6">
        {matchedProjects.map((project, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{project.title}</CardTitle>
              <CardDescription>{project.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center">
                <div className="space-x-2">
                  {project.techStack.map((tech, techIndex) => (
                    <Badge key={techIndex} variant="secondary">
                      {tech}
                    </Badge>
                  ))}
                </div>
                <span className="text-2xl font-bold text-red-500">
                  {project.similarity}% Match
                </span>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline">View Project</Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <div className="mt-8 text-center">
        <Button size="lg" className="bg-blue-900 hover:bg-blue-800 text-white">
          View Full Report
        </Button>
      </div>
    </div>
  );
};

export default Result;
