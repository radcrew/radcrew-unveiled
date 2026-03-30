import * as styles from "./styles";

interface ChatErrorBannerProps {
  message: string;
}

export const ChatErrorBanner = ({ message }: ChatErrorBannerProps) => (
  <p className={styles.root}>{message}</p>
);
