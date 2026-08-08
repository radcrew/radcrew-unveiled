import { ProjectCarousel } from "./ProjectCarousel";
import type { FeaturedProject } from "./static-data";

/**
 * Picks the right media for a project and nothing else. Shared so the pinned and
 * stacked portfolio layouts cannot drift on which projects get a carousel, a
 * single image, or nothing at all.
 */
export const ProjectMedia = ({ project }: { project: FeaturedProject }) => {
  if (project.images && project.images.length > 0) {
    return <ProjectCarousel title={project.title} images={project.images} />;
  }
  if (project.image) {
    return (
      <img
        src={project.image}
        alt={project.title}
        loading="lazy"
        decoding="async"
        className="h-full w-full object-cover transition-transform duration-1000 group-hover:scale-105"
      />
    );
  }
  return null;
};
