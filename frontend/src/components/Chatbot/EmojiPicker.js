import React from "react";

export default function EmojiPicker({ addEmoji }) {
  const emojis = ["😊","😂","😎","❤️","👍","🤔","😢","🎉","🙌","🔥"];
  return (
    <div className="emoji-picker">
      {emojis.map((e) => (
        <span key={e} onClick={() => addEmoji(e)}>{e}</span>
      ))}
    </div>
  );
}
