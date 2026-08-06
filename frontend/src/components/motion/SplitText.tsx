import { Fragment } from "react";
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
 * Each word gets its own `overflow-hidden` box to clip the slide-up, and the
 * space between words is a real text node *between* those boxes rather than a
 * margin. That keeps the DOM text identical to `text`, so the heading reads
 * normally to screen readers and extracts cleanly — no `aria-hidden` copy, and
 * no words running together.
 *
 * Under `prefers-reduced-motion` only the plain string is rendered.
 */
export const SplitText = ({ text, delay = 0, className }: SplitTextProps) => {
  const reduced = useReducedMotion();
  const words = text.split(" ");

  if (reduced) return <span className={className}>{text}</span>;

  return (
    <motion.span
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-80px" }}
      variants={{ visible: { transition: { staggerChildren: 0.06, delayChildren: delay } } }}
    >
      {words.map((word, i) => (
        <Fragment key={`${word}-${i}`}>
          <span className="inline-block overflow-hidden align-bottom">
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
          {i < words.length - 1 ? " " : null}
        </Fragment>
      ))}
    </motion.span>
  );
};
