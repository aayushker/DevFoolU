interface AIVerdict {
  verdict: string;
  model: string;
  status: string;
  projects_analyzed: number;
}

interface SimilarProject {
  _id: string;
  urlOfProject: string;
  nameOfProject: string;
  descriptionOfProject: string;
  problemSolved: string;
  challengesFaced: string;
  technologiesUsed: string[];
  similarity_score: number;
}

interface AIInsightsProps {
  aiVerdict: AIVerdict;
  similarProjects: SimilarProject[];
}

export default function AIInsights({
  aiVerdict,
  similarProjects,
}: AIInsightsProps) {
  if (!aiVerdict || aiVerdict.status !== "success") {
    return null;
  }

  // Parse the verdict text to extract key points
  const verdictLines = aiVerdict.verdict
    .split("\n")
    .filter((line) => line.trim());

  return (
    <div className="mt-8 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl shadow-lg overflow-hidden border border-purple-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <div>
              <h3 className="text-xl font-bold text-white">
                AI-Powered Insights
              </h3>
              <p className="text-purple-100 text-sm">
                Analyzed {aiVerdict.projects_analyzed} similar projects using{" "}
                {aiVerdict.model}
              </p>
            </div>
          </div>
          <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm font-medium">
            ✨ AI Analysis
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Verdict Sections */}
        <div className="space-y-4">
          {verdictLines.map((line, index) => {
            const trimmedLine = line.trim();

            // Check if it's a header (starts with *)
            if (trimmedLine.startsWith("*") && trimmedLine.includes("**")) {
              const headerText = trimmedLine.replace(/\*+/g, "").trim();
              const [title, ...contentParts] = headerText.split(":");
              const content = contentParts.join(":").trim();

              return (
                <div
                  key={index}
                  className="bg-white rounded-lg p-5 shadow-md border border-purple-100 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-1">
                      {title.toLowerCase().includes("similarity") && (
                        <svg
                          className="w-6 h-6 text-purple-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                          />
                        </svg>
                      )}
                      {title.toLowerCase().includes("key") && (
                        <svg
                          className="w-6 h-6 text-blue-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
                          />
                        </svg>
                      )}
                      {title.toLowerCase().includes("technology") && (
                        <svg
                          className="w-6 h-6 text-green-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                          />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-2">
                        {title}
                      </h4>
                      {content && (
                        <p className="text-gray-700 leading-relaxed">
                          {content}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            }

            return null;
          })}
        </div>

        {/* Technology Insights */}
        {similarProjects && similarProjects.length > 0 && (
          <div className="bg-white rounded-lg p-5 shadow-md border border-blue-100">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                />
              </svg>
              Common Technologies Found
            </h4>
            <div className="flex flex-wrap gap-2">
              {Array.from(
                new Set(
                  similarProjects
                    .flatMap((p) => p.technologiesUsed || [])
                    .filter(Boolean)
                )
              )
                .slice(0, 15)
                .map((tech, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full text-sm font-medium border border-blue-200"
                  >
                    {tech}
                  </span>
                ))}
            </div>
          </div>
        )}

        {/* Similarity Score Distribution */}
        {similarProjects && similarProjects.length > 0 && (
          <div className="bg-white rounded-lg p-5 shadow-md border border-green-100">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                />
              </svg>
              Similarity Distribution
            </h4>
            <div className="space-y-2">
              {similarProjects.slice(0, 5).map((project, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-700 font-medium truncate max-w-xs">
                        {project.nameOfProject}
                      </span>
                      <span className="text-sm font-semibold text-gray-900">
                        {(project.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${project.similarity_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Model Badge */}
        <div className="flex items-center justify-center gap-2 text-sm text-gray-600 pt-2">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <span>
            Powered by{" "}
            <strong className="text-purple-600">{aiVerdict.model}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
