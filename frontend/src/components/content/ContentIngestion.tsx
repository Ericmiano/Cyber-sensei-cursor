import { useState, useRef } from "react";
import { 
  Upload, 
  FileJson, 
  FileSpreadsheet, 
  Check, 
  AlertCircle, 
  Loader2,
  Plus,
  Trash2,
  Eye,
  Download,
  FileText
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface ContentItem {
  id: string;
  title: string;
  type: "module" | "lesson" | "quiz" | "exercise";
  status: "draft" | "published";
  createdAt: Date;
}

interface ModuleTemplate {
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  lessons: {
    title: string;
    duration: string;
    content: { type: string; content: string }[];
    quiz?: { question: string; options: string[]; correctIndex: number };
  }[];
}

const STORAGE_KEY = "cyber_sensei_custom_content";

export default function ContentIngestion() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedContent, setUploadedContent] = useState<ContentItem[]>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return [];
      }
    }
    return [];
  });
  const [previewData, setPreviewData] = useState<ModuleTemplate | null>(null);

  // Manual entry state
  const [manualModule, setManualModule] = useState({
    title: "",
    description: "",
    difficulty: "beginner" as const,
  });
  const [manualLessons, setManualLessons] = useState<{ title: string; content: string }[]>([
    { title: "", content: "" }
  ]);

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);

    try {
      const text = await file.text();
      let data: ModuleTemplate;

      if (file.name.endsWith(".json")) {
        data = JSON.parse(text);
      } else if (file.name.endsWith(".csv")) {
        // Basic CSV parsing
        const lines = text.split("\n").map(line => line.split(","));
        const headers = lines[0];
        data = {
          title: file.name.replace(".csv", ""),
          description: "Imported from CSV",
          difficulty: "intermediate",
          lessons: lines.slice(1).map((row, i) => ({
            title: row[0] || `Lesson ${i + 1}`,
            duration: row[1] || "15 min",
            content: [{ type: "text", content: row[2] || "" }],
          })),
        };
      } else {
        throw new Error("Unsupported file format. Please use JSON or CSV.");
      }

      setPreviewData(data);
      toast({
        title: "File Parsed Successfully",
        description: `Found ${data.lessons?.length || 0} lessons in "${data.title}"`,
      });
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Could not parse the file",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const confirmImport = () => {
    if (!previewData) return;

    const newItem: ContentItem = {
      id: Date.now().toString(),
      title: previewData.title,
      type: "module",
      status: "draft",
      createdAt: new Date(),
    };

    const updated = [...uploadedContent, newItem];
    setUploadedContent(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    
    // Also store the full module data
    const moduleData = localStorage.getItem("cyber_sensei_modules") || "{}";
    const modules = JSON.parse(moduleData);
    modules[newItem.id] = previewData;
    localStorage.setItem("cyber_sensei_modules", JSON.stringify(modules));

    setPreviewData(null);
    toast({
      title: "Content Imported!",
      description: `"${previewData.title}" has been added as a draft.`,
    });
  };

  const handleManualSave = () => {
    if (!manualModule.title.trim()) {
      toast({
        title: "Title Required",
        description: "Please enter a module title.",
        variant: "destructive",
      });
      return;
    }

    const moduleData: ModuleTemplate = {
      ...manualModule,
      lessons: manualLessons
        .filter(l => l.title.trim())
        .map(l => ({
          title: l.title,
          duration: "15 min",
          content: [{ type: "text", content: l.content }],
        })),
    };

    const newItem: ContentItem = {
      id: Date.now().toString(),
      title: manualModule.title,
      type: "module",
      status: "draft",
      createdAt: new Date(),
    };

    const updated = [...uploadedContent, newItem];
    setUploadedContent(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

    // Store full module data
    const modules = JSON.parse(localStorage.getItem("cyber_sensei_modules") || "{}");
    modules[newItem.id] = moduleData;
    localStorage.setItem("cyber_sensei_modules", JSON.stringify(modules));

    // Reset form
    setManualModule({ title: "", description: "", difficulty: "beginner" });
    setManualLessons([{ title: "", content: "" }]);

    toast({
      title: "Module Created!",
      description: `"${manualModule.title}" has been saved as a draft.`,
    });
  };

  const addLesson = () => {
    setManualLessons([...manualLessons, { title: "", content: "" }]);
  };

  const removeLesson = (index: number) => {
    setManualLessons(manualLessons.filter((_, i) => i !== index));
  };

  const updateLesson = (index: number, field: "title" | "content", value: string) => {
    const updated = [...manualLessons];
    updated[index][field] = value;
    setManualLessons(updated);
  };

  const deleteContent = (id: string) => {
    const updated = uploadedContent.filter(c => c.id !== id);
    setUploadedContent(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    
    const modules = JSON.parse(localStorage.getItem("cyber_sensei_modules") || "{}");
    delete modules[id];
    localStorage.setItem("cyber_sensei_modules", JSON.stringify(modules));

    toast({ title: "Content Deleted" });
  };

  const togglePublish = (id: string) => {
    const updated = uploadedContent.map(c => 
      c.id === id ? { ...c, status: c.status === "draft" ? "published" as const : "draft" as const } : c
    );
    setUploadedContent(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const downloadTemplate = () => {
    const template: ModuleTemplate = {
      title: "Module Title",
      description: "Module description here",
      difficulty: "intermediate",
      lessons: [
        {
          title: "Lesson 1 Title",
          duration: "20 min",
          content: [
            { type: "text", content: "Lesson content goes here..." },
            { type: "tip", content: "Pro tip: This is a helpful hint!" }
          ],
          quiz: {
            question: "Quiz question?",
            options: ["Option A", "Option B", "Option C", "Option D"],
            correctIndex: 0
          }
        }
      ]
    };

    const blob = new Blob([JSON.stringify(template, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "module_template.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <Card className="bg-card/50 border-border/50 interactive-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Upload className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="font-cyber text-xl text-primary">
                  CONTENT INGESTION
                </CardTitle>
                <CardDescription>
                  Import or create custom training modules
                </CardDescription>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={downloadTemplate} className="gap-2">
              <Download className="h-4 w-4" />
              Template
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          <Tabs defaultValue="upload" className="space-y-4">
            <TabsList className="bg-muted/50">
              <TabsTrigger value="upload" className="gap-2">
                <FileJson className="h-4 w-4" />
                File Upload
              </TabsTrigger>
              <TabsTrigger value="manual" className="gap-2">
                <FileText className="h-4 w-4" />
                Manual Entry
              </TabsTrigger>
            </TabsList>

            {/* File Upload Tab */}
            <TabsContent value="upload" className="space-y-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".json,.csv"
                onChange={handleFileUpload}
                className="hidden"
              />

              <div
                onClick={handleFileSelect}
                className={cn(
                  "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all",
                  "border-border/50 hover:border-primary/50 hover:bg-primary/5",
                  isUploading && "pointer-events-none opacity-50"
                )}
              >
                {isUploading ? (
                  <Loader2 className="h-10 w-10 mx-auto text-primary animate-spin" />
                ) : (
                  <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-4" />
                )}
                <p className="text-foreground font-medium mb-1">
                  {isUploading ? "Processing..." : "Click to upload or drag and drop"}
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports JSON and CSV files
                </p>
                <div className="flex justify-center gap-2 mt-4">
                  <Badge variant="outline" className="gap-1">
                    <FileJson className="h-3 w-3" /> JSON
                  </Badge>
                  <Badge variant="outline" className="gap-1">
                    <FileSpreadsheet className="h-3 w-3" /> CSV
                  </Badge>
                </div>
              </div>

              {/* Preview Section */}
              {previewData && (
                <Card className="bg-primary/5 border-primary/30 animate-fade-in">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{previewData.title}</CardTitle>
                      <Badge className="bg-neon-orange/20 text-neon-orange">Preview</Badge>
                    </div>
                    <CardDescription>{previewData.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4 mb-4">
                      <Badge variant="outline">{previewData.difficulty}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {previewData.lessons?.length || 0} lessons
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={confirmImport} className="flex-1 neon-glow-cyan">
                        <Check className="h-4 w-4 mr-2" />
                        Import Content
                      </Button>
                      <Button variant="outline" onClick={() => setPreviewData(null)}>
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Manual Entry Tab */}
            <TabsContent value="manual" className="space-y-4">
              <div className="grid gap-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Module Title</Label>
                    <Input
                      placeholder="e.g., Advanced Threat Detection"
                      value={manualModule.title}
                      onChange={(e) => setManualModule({ ...manualModule, title: e.target.value })}
                      className="bg-muted/30"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Difficulty</Label>
                    <select
                      value={manualModule.difficulty}
                      onChange={(e) => setManualModule({ ...manualModule, difficulty: e.target.value as any })}
                      className="w-full h-10 px-3 rounded-md border border-input bg-muted/30 text-foreground"
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Describe what learners will gain from this module..."
                    value={manualModule.description}
                    onChange={(e) => setManualModule({ ...manualModule, description: e.target.value })}
                    className="bg-muted/30 min-h-[80px]"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Lessons</Label>
                    <Button variant="outline" size="sm" onClick={addLesson} className="gap-1">
                      <Plus className="h-4 w-4" /> Add Lesson
                    </Button>
                  </div>

                  <ScrollArea className="max-h-[300px]">
                    <div className="space-y-3 pr-4">
                      {manualLessons.map((lesson, index) => (
                        <Card key={index} className="bg-muted/20 border-border/30 p-4">
                          <div className="flex items-start gap-3">
                            <span className="w-6 h-6 rounded bg-primary/20 text-primary text-xs flex items-center justify-center flex-shrink-0 mt-1">
                              {index + 1}
                            </span>
                            <div className="flex-1 space-y-3">
                              <Input
                                placeholder="Lesson title"
                                value={lesson.title}
                                onChange={(e) => updateLesson(index, "title", e.target.value)}
                                className="bg-muted/30"
                              />
                              <Textarea
                                placeholder="Lesson content..."
                                value={lesson.content}
                                onChange={(e) => updateLesson(index, "content", e.target.value)}
                                className="bg-muted/30 min-h-[60px]"
                              />
                            </div>
                            {manualLessons.length > 1 && (
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => removeLesson(index)}
                                className="text-destructive hover:text-destructive"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </div>

                <Button onClick={handleManualSave} className="neon-glow-cyan">
                  <Check className="h-4 w-4 mr-2" />
                  Save Module
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Uploaded Content List */}
      {uploadedContent.length > 0 && (
        <Card className="bg-card/50 border-border/50">
          <CardHeader>
            <CardTitle className="font-cyber text-lg text-primary">
              YOUR CONTENT ({uploadedContent.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedContent.map((item, index) => (
                <div
                  key={item.id}
                  className={cn(
                    "flex items-center justify-between p-4 rounded-lg border transition-all",
                    "bg-muted/20 border-border/30 hover:border-primary/30",
                    "animate-slide-up"
                  )}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-primary" />
                    <div>
                      <h4 className="font-medium">{item.title}</h4>
                      <p className="text-xs text-muted-foreground">
                        Created {new Date(item.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className={cn(
                        item.status === "published"
                          ? "text-neon-green border-neon-green/30"
                          : "text-neon-orange border-neon-orange/30"
                      )}
                    >
                      {item.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => togglePublish(item.id)}
                      title={item.status === "draft" ? "Publish" : "Unpublish"}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => deleteContent(item.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
