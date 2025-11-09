# Getting Started with Betty

## First Time Setup

### 1. Environment Setup

Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. API Configuration

Betty works with both Anthropic Claude and OpenAI models.

**Option A: Using Anthropic Claude (Recommended)**

1. Get API key from https://console.anthropic.com/
2. Create `.streamlit/secrets.toml`:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```

**Option B: Using OpenAI**

1. Get API key from https://platform.openai.com/
2. Add to `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```

### 3. Run Betty

```bash
streamlit run betty_app.py
```

Betty will open in your browser at http://localhost:8501

## Understanding the Demo Data

Betty comes pre-loaded with TechCorp Electronics data:

- **Company**: Fictional IoT manufacturer
- **13 Capability Clusters**: Acquire Customer, Business Effectiveness, etc.
- **558 Outcomes**: Strategic goals across all capabilities
- **5 Focus Areas**: Change Control, Product Data, Requirements, Design, Data & AI

## Example Conversations

### Strategic Planning
**You**: "What are the top outcomes for customer acquisition?"
**Betty**: *Explains tier 1-5 outcomes with hierarchy*

### Project Analysis
**You**: "Which projects have the highest impact?"
**Betty**: *Analyzes project impacts across capabilities*

### Framework Learning
**You**: "Explain outcome-based thinking"
**Betty**: *Teaches OBT methodology with examples*

## Customizing for Your Organization

### Replace Demo Data

1. **Update GPS Outcomes**
   - Edit `docs/TechCorp_Data/GPS_2.0_Master.json`
   - Maintain JSON structure
   - Update all 'TechCorp' references to your company

2. **Add Your Documents**
   - Place Word/PDF files in `docs/TechCorp_Data/`
   - Betty will automatically index them
   - Supports .docx, .pdf, .txt, .xlsx

3. **Customize System Prompt**
   - Edit `system_prompt_v4.3.txt`
   - Adjust Betty's expertise and tone
   - Add domain-specific knowledge

## Troubleshooting

### "Collection does not exist" Error
- Click "🔄 Refresh Knowledge Base" in sidebar
- Wait for indexing to complete

### Slow Responses
- Check API key is valid
- Try reducing response length in sidebar
- Use faster model (Claude Haiku)

### No Search Results
- Verify documents are in docs/TechCorp_Data/
- Check file formats are supported
- Rebuild knowledge base

## Performance Tips

1. **Model Selection**
   - Claude 3.5 Sonnet: Best quality
   - Claude 3 Haiku: Fastest responses
   - GPT-4: Alternative provider

2. **Response Length**
   - Adjust max tokens in sidebar
   - Lower values = faster responses

3. **Knowledge Base**
   - Keep docs organized in folders
   - Remove unnecessary files
   - Refresh after changes

## Next Steps

- Review evaluation framework in `evaluation/`
- Explore capability clusters in demo data
- Customize system prompt for your domain
- Add your organization's documents

## Support

For questions: [your-email@example.com]

## Learn More

- [Outcome-Based Thinking](docs/TechCorp_Data/7.0_About_OBT/)
- [GPS Framework](docs/TechCorp_Data/7.0_About_OBT/)
- [Evaluation Results](evaluation/results/)
