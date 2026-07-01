export const PAPER_GROUPS = [
  {
    label: 'Language Models',
    papers: [
      { id: '1706.03762', name: 'Attention Is All You Need', year: 2017 },
      { id: '1810.04805', name: 'BERT',                      year: 2018 },
      { id: '1910.10683', name: 'T5',                        year: 2019 },
      { id: '2005.14165', name: 'GPT-3',                     year: 2020 },
      { id: '2303.08774', name: 'GPT-4',                     year: 2023 },
      { id: '2302.13971', name: 'LLaMA',                     year: 2023 },
      { id: '2307.09288', name: 'LLaMA 2',                   year: 2023 },
      { id: '2310.06825', name: 'Mistral 7B',                year: 2023 },
      { id: '2312.00752', name: 'Mamba',                     year: 2023 },
    ],
  },
  {
    label: 'Alignment & Fine-tuning',
    papers: [
      { id: '2106.09685', name: 'LoRA',              year: 2021 },
      { id: '2203.02155', name: 'InstructGPT',       year: 2022 },
      { id: '2305.18290', name: 'DPO',               year: 2023 },
      { id: '2212.08073', name: 'Constitutional AI', year: 2022 },
    ],
  },
  {
    label: 'Vision & Generation',
    papers: [
      { id: '1512.03385', name: 'ResNet',           year: 2015 },
      { id: '2010.11929', name: 'ViT',              year: 2020 },
      { id: '2103.00020', name: 'CLIP',             year: 2021 },
      { id: '2006.11239', name: 'DDPM',             year: 2020 },
      { id: '2112.10752', name: 'Stable Diffusion', year: 2021 },
      { id: '2204.06125', name: 'DALL-E 2',         year: 2022 },
      { id: '2304.02643', name: 'Segment Anything', year: 2023 },
    ],
  },
  {
    label: 'Reasoning & Retrieval',
    papers: [
      { id: '2201.11903', name: 'Chain of Thought', year: 2022 },
      { id: '2005.11401', name: 'RAG',              year: 2020 },
      { id: '2212.04356', name: 'Whisper',          year: 2022 },
      { id: '2205.14135', name: 'Flash Attention',  year: 2022 },
      { id: '2107.03374', name: 'Codex',            year: 2021 },
    ],
  },
  {
    label: 'Foundations',
    papers: [
      { id: '1406.2661', name: 'GAN',      year: 2014 },
      { id: '1301.3781', name: 'Word2Vec', year: 2013 },
    ],
  },
]

export const EXAMPLE_QUESTIONS = [
  'Which papers extended this work?',
  'How was this paper used later?',
  'Show me papers that disagreed with this work.',
  'Summarize the key contributions that cite this paper.',
  'What papers challenged or contradicted the claims?',
  'List the most influential papers that built on this.',
]

export const LOADING_MSGS = [
  'Building citation graph…',
  'Routing to agent…',
  'Calling LLM…',
  'Synthesising response…',
]
