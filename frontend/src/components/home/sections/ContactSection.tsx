import { useState } from "react";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@components/ui/form";
import { Input } from "@components/ui/input";
import { Textarea } from "@components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@components/ui/select";
import { useToast } from "@/hooks/useToast";
import { getWeb3FormsAccessKey, submitWeb3Form } from "@/lib/web3forms-submit";

const contactSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email address"),
  company: z.string().optional(),
  projectType: z.enum(["fullstack", "web3", "ai", "other"], {
    required_error: "Please select a project type",
  }),
  message: z.string().min(10, "Please provide more details about your project"),
});

type ContactFormValues = z.infer<typeof contactSchema>;

export const ContactSection = () => {
  const { toast } = useToast();
  const [contactPending, setContactPending] = useState(false);

  const form = useForm<ContactFormValues>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: "",
      email: "",
      company: "",
      projectType: undefined,
      message: "",
    },
  });

  async function onSubmit(data: ContactFormValues) {
    if (!getWeb3FormsAccessKey()) {
      toast({
        title: "Email us directly",
        description: "Set VITE_WEB3FORMS_ACCESS_KEY for the form, or write to code@radcrew.org.",
        variant: "destructive",
      });
      return;
    }
    setContactPending(true);
    try {
      const lines = [
        `Name: ${data.name}`,
        `Email: ${data.email}`,
        data.company ? `Company: ${data.company}` : "",
        `Project type: ${data.projectType}`,
        "",
        data.message,
      ].filter(Boolean);
      await submitWeb3Form({
        subject: "RadCrew — website inquiry",
        from_name: data.name,
        email: data.email,
        message: lines.join("\n"),
      });
      toast({
        title: "Inquiry received.",
        description: "We'll be in touch shortly to schedule a discovery call.",
      });
      form.reset();
    } catch {
      toast({
        title: "Something went wrong.",
        description: "Please try again later or email code@radcrew.org.",
        variant: "destructive",
      });
    } finally {
      setContactPending(false);
    }
  }

  return (
    <section id="contact" className="relative border-t border-border bg-background px-6 py-32 lg:px-12">
      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-16 text-center"
        >
          <h2 className="mb-6 font-serif text-5xl leading-tight text-foreground md:text-7xl">
            Tell us what you&apos;re <span className="italic text-primary">building.</span>
          </h2>
          <p className="mx-auto max-w-2xl text-xl font-light text-muted-foreground">
            A private invitation to collaborate. Fill out the form and we&apos;ll arrange a technical discovery session.
          </p>
        </motion.div>

        <div className="border border-border bg-muted p-8 shadow-sm md:p-12">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <div className="grid gap-8 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                        Full Name
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Jane Doe"
                          {...field}
                          className="h-14 rounded-none border-border bg-background font-light focus-visible:ring-primary"
                          data-testid="contact-name"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                        Email Address
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder="jane@company.com"
                          {...field}
                          className="h-14 rounded-none border-border bg-background font-light focus-visible:ring-primary"
                          data-testid="contact-email"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid gap-8 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="company"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                        Company (Optional)
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Company Inc."
                          {...field}
                          className="h-14 rounded-none border-border bg-background font-light focus-visible:ring-primary"
                          data-testid="contact-company"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="projectType"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                        Project Type
                      </FormLabel>
                      <Select onValueChange={field.onChange} value={field.value ?? ""}>
                        <FormControl>
                          <SelectTrigger
                            className="h-14 rounded-none border-border bg-background font-light data-[state=open]:text-foreground focus:ring-primary text-muted-foreground"
                            data-testid="contact-project-type"
                          >
                            <SelectValue placeholder="Select type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="rounded-none border-border">
                          <SelectItem value="fullstack" className="cursor-pointer font-light">
                            Full Stack Engineering
                          </SelectItem>
                          <SelectItem value="web3" className="cursor-pointer font-light">
                            Web3 / Blockchain
                          </SelectItem>
                          <SelectItem value="ai" className="cursor-pointer font-light">
                            AI / Machine Learning
                          </SelectItem>
                          <SelectItem value="other" className="cursor-pointer font-light">
                            Other
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="message"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                      Project Details
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Tell us about the vision, timeline, and budget..."
                        className="min-h-[150px] resize-y rounded-none border-border bg-background font-light focus-visible:ring-primary"
                        {...field}
                        data-testid="contact-message"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button
                type="submit"
                className="h-16 w-full rounded-none bg-primary text-sm font-light uppercase tracking-widest text-primary-foreground transition-all hover:bg-primary/90"
                disabled={contactPending}
                data-testid="contact-submit"
              >
                {contactPending ? "Submitting..." : "Submit Inquiry"}
              </Button>
            </form>
          </Form>
        </div>
      </div>
    </section>
  );
};
