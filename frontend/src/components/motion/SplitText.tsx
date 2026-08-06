import { motion, useReducedMotion } from "framer-motion";

type SplitTextProps = {
  text: string;
  delay?: number;
  className?: string;
};

/**
 * Word-by-word headline reveal. Renders an inline span, so the caller keeps
 * control of the heading tag.
 *
 * The animated words are `aria-hidden` and the full string is repeated in an
 * `sr-only` span: split into per-word elements, screen readers otherwise
 * announce the headline one word per pause. Under `prefers-reduced-motion`
 * only the plain string is rendered.
 */
export const SplitText = ({ text, delay = 0, className }: SplitTextProps) => {
  const reduced = useReducedMotion();
  const words = text.split(" ");

  if (reduced) return <span className={className}>{text}</span>;

  return (
    <span className={className}>
      <span className="sr-only">{text}</span>
      <motion.span
        aria-hidden="true"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        variants={{ visible: { transition: { staggerChildren: 0.06, delayChildren: delay } } }}
      >
        {words.map((word, i) => (
          <span
            key={`${word}-${i}`}
            className={`inline-block overflow-hidden align-bottom ${i < words.length - 1 ? "mr-[0.25em]" : ""}`}
          >
            <motion.span
              className="inline-block"
              variants={{
                hidden: { y: "100%", opacity: 0 },
                visible: { y: "0%", opacity: 1, transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } },
              }}
            >
              {word}
            </motion.span>
          </span>
        ))}
      </motion.span>
    </span>
  );
};
