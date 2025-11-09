# Betty - Outcome-Based Thinking AI Assistant

**An AI-powered assistant for Outcome-Based Thinking (OBT) and GPS Framework implementation**

## Overview

Betty is an intelligent assistant designed to help organizations implement Outcome-Based Thinking (OBT) methodologies and navigate complex organizational frameworks using the GPS (Goal-Pain-Solution) approach.

### Key Features

- **Outcome-Based Framework Navigation** - Intelligent querying across 13 capability clusters and 558+ outcomes
- **GPS Methodology** - Goal-Pain-Solution framework for strategic planning
- **Multi-Model AI Support** - Compatible with Claude (Anthropic), GPT-4 (OpenAI), and other LLMs
- **RAG Architecture** - Vector-based knowledge retrieval using ChromaDB
- **Interactive Streamlit UI** - User-friendly interface with conversation history
- **Evaluation Framework** - Comprehensive testing and validation system

### Demo Company: TechCorp Electronics

This repository includes synthetic data for **TechCorp Electronics**, a fictional mid-sized industrial IoT manufacturer. All data, metrics, and scenarios are completely synthetic and created for demonstration purposes.

## Quick Start

### Prerequisites

- Python 3.9+
- API key for Claude (Anthropic) or OpenAI

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/betty-obt-assistant.git
   cd betty-obt-assistant
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**

   Create `.streamlit/secrets.toml`:
   ```toml
   ANTHROPIC_API_KEY = "your-anthropic-api-key"
   # or
   OPENAI_API_KEY = "your-openai-api-key"
   ```

5. **Run Betty**
   ```bash
   streamlit run betty_app.py
   ```

6. **Open browser** to http://localhost:8501

## Architecture

### Components

```
betty-obt-assistant/
├── betty_app.py              # Main Streamlit application
├── utils/
│   ├── vector_store.py       # ChromaDB vector database
│   ├── document_processor.py # Document loading & chunking
│   └── ai_providers.py       # LLM integrations
├── docs/
│   └── TechCorp_Data/        # Synthetic demo data
│       ├── GPS_2.0_Master.json
│       ├── 1.0_Change_Control_Management/
│       ├── 2.0_Product_Data_Management/
│       ├── 3.0_Requirements_Management/
│       ├── 4.0_Design_Management/
│       └── 5.0_Data_and_AI/
└── evaluation/
    ├── betty_evaluation_v5.yml    # Test cases
    ├── run_evaluation_v5.py       # Evaluation runner
    └── generate_html_report_v5.py # Report generator
```

### Technology Stack

- **Framework**: Streamlit
- **Vector Database**: ChromaDB
- **LLM Integration**: LangChain
- **Document Processing**: python-docx, openpyxl, PyPDF2
- **AI Models**: Claude 3.5 Sonnet, GPT-4

## Usage Examples

### Example Queries

**Strategic Questions:**
- "What are the highest priority outcomes for customer acquisition?"
- "Compare Design Management with Requirements Management capabilities"
- "What pain points does TechCorp face in product data management?"

**Project Analysis:**
- "What projects have the highest capability impact?"
- "Show me the KPIs for change control management"
- "What is the maturity level for data and AI capabilities?"

**Framework Navigation:**
- "Explain the GPS framework"
- "What is outcome-based thinking?"
- "How do capabilities relate to outcomes?"

## Customization Guide

### Adapting for Your Organization

1. **Replace Synthetic Data**
   - Update `docs/TechCorp_Data/GPS_2.0_Master.json` with your outcomes
   - Add your capability definitions, projects, and pain points
   - Keep the same JSON structure for compatibility

2. **Customize System Prompt**
   - Edit `system_prompt_v4.3.txt`
   - Adjust tone, expertise, and response style
   - Add domain-specific knowledge

3. **Configure LLM**
   - Choose your preferred model in sidebar
   - Adjust temperature and parameters
   - Set response length limits

4. **Modify UI**
   - Streamlit configuration in `betty_app.py`
   - Custom styling in Streamlit config
   - Add/remove sidebar options

## Evaluation & Testing

Run comprehensive evaluation suite:

```bash
cd evaluation
python run_evaluation_v5.py
python generate_html_report_v5.py
```

View results in `evaluation/results/` directory.

### Evaluation Metrics

- **Accuracy**: Response correctness
- **Completeness**: Coverage of key points
- **Hallucination Detection**: Factual accuracy
- **Source Attribution**: Proper citations
- **Response Quality**: Overall helpfulness

## Performance

- **Evaluation Score**: 0.740/1.0 (74%)
- **Response Time**: < 3 seconds average
- **Knowledge Base**: 558 outcomes, 13 capability clusters
- **Vector Dimensions**: 1536 (OpenAI embeddings)

## Contributing

This is a demonstration project. For bugs or questions, contact the maintainer via email.

## Data Privacy

**Important**: This repository contains only synthetic data. All company names, projects, metrics, and scenarios are fictional and created for demonstration purposes.

## License

[Your chosen license - MIT, Apache 2.0, Proprietary, etc.]

## Support

For questions or issues, contact: [your-email@example.com]

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Anthropic Claude](https://www.anthropic.com/) and [OpenAI](https://openai.com/)
- Vector search by [ChromaDB](https://www.trychroma.com/)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-08
**Status**: Production Ready
