import { useEffect, useRef, useState, type FormEvent } from "react";
import { sendChatMessage } from "@/lib/chatbot-api";
import { ChatFloatingButton } from "./ChatFloatingButton";

export function ChatWidget() {
  async function sendMessage() {
  }

  return (
    <>
      <ChatFloatingButton onOpen={() => setOpen(true)} />
    </>
  );
}
