## **Comet-Labs: AI-Powered Commit Messages**

✨ **Comet-Labs** is a powerful and user-friendly CLI tool designed to generate smarter, AI-driven commit messages and streamline your development workflow. With optional Jira integration and lightweight NLP-based summarization, it’s a must-have for developers looking to save time and improve code clarity. 🚀

---

### **Features**

- **AI-Driven Commit Messages**: Generate commit messages with detailed descriptions using OpenAI or a free AI fallback.
- **Jira Integration**: Link commit messages to Jira tickets effortlessly.
- **Lightweight NLP Fallback**: For users without OpenAI access, enjoy basic summarization powered by lightweight NLP tools.
- **Intuitive CLI**: Easy-to-use commands for generating, customizing, and committing changes.
- **Open Source**: Built for the community, by the community.

---

### **Installation**

#### **Prerequisites**
- Python >= 3.8
- Pip

#### **Install from PyPI**
```bash
pip install comet-labs
```

---

### **Quick Start**

#### **1. Initialize Comet-Labs**
Set up your environment with a simple interactive initialization process:
```bash
comet-labs initialize
```

During initialization:
- You'll be prompted to enter your **OpenAI API key** (recommended for advanced features).
- Optionally, configure **Jira integration** to link commit messages with Jira tickets.
- Ensure necessary NLP resources (like TextBlob) are downloaded automatically.

#### **2. Generate Commit Messages**
Stage your changes and run:
```bash
comet-labs run
```

Comet-Labs will:
- Analyze the changes in your git repository.
- Generate a concise commit message and detailed description.

#### **3. Dedicate Credits (Optional)**
To view project credits and a special dedication:
```bash
comet-labs credits
```

---

### **Commands**

| Command                 | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `comet-labs initialize` | Interactive setup for OpenAI API, Jira integration, and NLP resources.     |
| `comet-labs run`        | Analyze git changes and generate commit messages.                          |
| `comet-labs credits`    | View project credits.|

---

### **Example Workflow**

#### **Generating a Commit Message**
1. Stage your changes:
   ```bash
   git add .
   ```

2. Run Comet-Labs:
   ```bash
   comet-labs run
   ```

3. Example Output:
   ```plaintext
   AI-Generated Commit Information:
   Message: "Update example script"

   Brief Description:
   - Modified imports.
   - Updated print statement.

   Detailed Description:
   - Changed the imports in example.py to include 'sys' and 'requests'.
   - Replaced the print statement to output 'Hello, GPT-3' instead of 'Hello World'.

   File Changes:
   - example.py: Modified imports and print statement.
   ```

4. Proceed with push (the commit has already been created at this point):
   ```bash
   git push
   ```

---

### **Configuration Options**

#### **Environment Variables**
Comet-Labs uses the following environment variables:

| Variable          | Description                            |
|-------------------|----------------------------------------|
| `OPENAI_API_KEY`  | Your OpenAI API key for GPT features.  |
| `JIRA_BASE_URL`   | Jira base URL (e.g., `https://example.atlassian.net`). |
| `JIRA_USERNAME`   | Jira username or email.               |
| `JIRA_API_TOKEN`  | API token for Jira authentication.    |

You can manage these variables in a `.env` file.

---

### **Lightweight AI Fallback**

For users without an OpenAI API key, Comet-Labs leverages **TextBlob** for basic NLP-based summarization. While results are not as detailed as OpenAI's GPT models, they provide a useful alternative for generating commit messages.

---

### **Contributing**

We welcome contributions to improve Comet-Labs! ❤️

#### **Getting Started**
1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/Sahilsingh0808/comet.git
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run tests:
   ```bash
   pytest
   ```

#### **Want to Help?**
- Report bugs or suggest features via [GitHub Issues](https://github.com/Sahilsingh0808/comet/issues).
- Submit a pull request with your improvements.

---

### **FAQ**

#### Q: What if I don’t have an OpenAI API key?
A: No problem! Comet-Labs will use a free AI fallback powered by TextBlob for lightweight commit message generation.

#### Q: Can I skip Jira integration during initialization?
A: Yes! Jira integration is optional and can be configured later by re-running `comet-labs initialize`.

#### Q: Does Comet-Labs store my API keys or credentials?
A: No, we respect your privacy. All keys are securely stored locally in a `.env` file.

---

### **License**

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

### **Links**

- **GitHub Repository**: [Comet-Labs on GitHub](https://github.com/Sahilsingh0808/comet)
- **PyPI Package**: [Comet-Labs on PyPI](https://pypi.org/project/comet-labs)
- **Issues & Feedback**: [Report an Issue](https://github.com/Sahilsingh0808/comet/issues)

---

Let me know if you'd like to customize this further! 🚀