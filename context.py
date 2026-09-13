def load_context(context_dir):
    """
    Read Context from the context_files folder.
    Deterministic: same files on disk always produce the same string.
    """
    context_content_list = []
    context_str = ""
    for md_file in context_dir.glob("**/*.md"):
        try:
            rel_path = md_file.relative_to(context_dir)
            text = md_file.read_text(encoding="utf-8")
            context_content_list.append(f"--- FILE: {rel_path} ---\n{text}\n")
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    if context_content_list:
        context_str = "\n".join(context_content_list)
    return context_str
