"""Seed IPCC AR6 key findings and NDC summaries into source_documents / document_chunks.

Run with:
    poetry run python -m scripts.seed_docs

Idempotent: skips source_type if already present.
"""
import re
import sys
from typing import Optional

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.models.source_document import SourceDocument


# ---------------------------------------------------------------------------
# Raw documents
# ---------------------------------------------------------------------------

IPCC_AR6_FINDINGS = [
    {
        "title": "AR6 SPM: Observed Warming",
        "content": (
            "Human-induced climate change is already affecting many weather and climate "
            "extremes in every region across the globe. Evidence of observed changes in "
            "extremes such as heatwaves, heavy precipitation, droughts, and tropical cyclones, "
            "and their attribution to human influence, has strengthened since the IPCC Fifth "
            "Assessment Report (AR5). Global surface temperature has increased faster since "
            "1970 than in any other 50-year period over at least the last 2000 years."
        ),
    },
    {
        "title": "AR6 SPM: 1.5°C and 2°C Thresholds",
        "content": (
            "Global surface temperature will continue to increase until at least the "
            "mid-century under all emissions scenarios considered. Global warming of 1.5°C "
            "and 2°C will be exceeded during the 21st century unless deep reductions in "
            "CO2 and other greenhouse gas emissions occur in the coming decades. "
            "Limiting global warming to 1.5°C requires net zero CO2 emissions globally "
            "in the early 2050s and deep reductions in other greenhouse gas emissions."
        ),
    },
    {
        "title": "AR6 SPM: Irreversible Changes",
        "content": (
            "Many changes due to past and future greenhouse gas emissions are irreversible "
            "for centuries to millennia, especially changes in the ocean, ice sheets and "
            "global sea level. Mountain and polar glaciers are committed to continue melting "
            "for decades or centuries. Sea level rise is committed even if emissions "
            "are sharply reduced; by 2100, global mean sea level could rise 0.28–1.01 m "
            "under high-emissions scenarios."
        ),
    },
    {
        "title": "AR6 SPM: Carbon Budget",
        "content": (
            "From a physical science perspective, limiting human-induced global warming "
            "to a specific level requires limiting cumulative CO2 emissions, reaching at "
            "least net zero CO2 emissions, along with strong reductions in other greenhouse "
            "gas emissions. The remaining carbon budget consistent with limiting warming to "
            "1.5°C with 50% probability is about 500 GtCO2 as of January 2020."
        ),
    },
    {
        "title": "AR6 SPM: Methane and Non-CO2 Gases",
        "content": (
            "Strong, rapid, and sustained reductions in methane emissions would also limit "
            "the warming effect resulting from declining aerosol pollution and would improve "
            "air quality. Scenarios that limit global warming to 1.5°C with no or limited "
            "overshoot involve strong reductions in CH4 of around 34% by 2030 relative to "
            "2019 levels."
        ),
    },
    {
        "title": "AR6 SPM: Adaptation Limits",
        "content": (
            "With increasing global warming, losses and damages will increase and "
            "additional human and natural systems will reach adaptation limits. "
            "Soft limits to adaptation can be overcome with greater resources and "
            "better knowledge, but hard limits cannot be overcome by adaptation alone. "
            "Some ecosystems and human communities are already at or beyond adaptation limits."
        ),
    },
    {
        "title": "AR6 SPM: Ecosystem Impacts",
        "content": (
            "Climate change has adversely affected food security and terrestrial ecosystems. "
            "Approximately 3.3–3.6 billion people live in contexts that are highly vulnerable "
            "to climate change. Climate and weather extremes are increasingly driving "
            "displacement in Africa, Asia, North America, and Central America. "
            "Ocean warming, ocean acidification, and loss of oxygen have compounded "
            "the adverse effects of fishing on marine ecosystems."
        ),
    },
    {
        "title": "AR6 SPM: Mitigation Pathways",
        "content": (
            "In mitigation pathways limiting warming to 1.5°C with no or limited overshoot, "
            "the global use of coal is reduced by 67–82% (relative to 2019) by 2030 and "
            "of oil by 12–20% by 2030. The use of low-emission sources of electricity "
            "generation increases substantially to 43–73% of electricity generation by 2030. "
            "Global net CO2 emissions are reduced by 48% to 69% by 2030 in these pathways."
        ),
    },
    {
        "title": "AR6 SPM: Finance and Investment",
        "content": (
            "The global stock of public and private financial capital directed toward "
            "fossil fuels still exceeds that directed toward climate change mitigation "
            "and adaptation. Available capital and global investment are sufficient to "
            "close investment gaps but there are barriers to redirecting financial flows. "
            "Mitigation finance would need to increase by a factor of three to six by 2030 "
            "to limit warming to below 2°C."
        ),
    },
    {
        "title": "AR6 SPM: Land Use and Agriculture",
        "content": (
            "Agriculture, Forestry and Other Land Use (AFOLU) currently accounts for "
            "approximately 22% of global greenhouse gas emissions. Reducing deforestation, "
            "improving land management, and restoring ecosystems could contribute up to "
            "30% of global mitigation by 2030. Dietary shifts towards more plant-based "
            "foods in high-emission settings can significantly reduce land-related emissions."
        ),
    },
    {
        "title": "AR6 SPM: Urban Systems",
        "content": (
            "Urban areas are hotspots of climate risk and vulnerability. Cities currently "
            "account for more than 70% of global CO2 emissions from final energy use. "
            "Ambitious mitigation in urban areas—driven by policy, technology, and social "
            "transformation—could reduce urban greenhouse gas emissions by 50–80% in 2050 "
            "compared to today."
        ),
    },
    {
        "title": "AR6 SPM: Renewable Energy Transition",
        "content": (
            "Unit costs for solar energy have fallen 85% since 2010, wind power 55%, "
            "and lithium-ion batteries 85%. Solar and wind power have grown rapidly "
            "and are now the cheapest sources of new electricity generation in most "
            "regions. This cost reduction has accelerated deployment and created new "
            "opportunities for electrification of transport, heating, and industry."
        ),
    },
    {
        "title": "AR6 SPM: Carbon Dioxide Removal",
        "content": (
            "Carbon dioxide removal (CDR) is needed to achieve net zero CO2 and GHG "
            "emissions globally. Options include afforestation, reforestation, soil "
            "carbon sequestration, bioenergy with carbon capture and storage (BECCS), "
            "enhanced weathering, and direct air carbon capture and storage (DACCS). "
            "All CDR methods have side effects and require careful governance."
        ),
    },
    {
        "title": "AR6 SPM: Health Impacts",
        "content": (
            "Climate change is adversely affecting human health, causing increases in "
            "heat-related mortality and morbidity and increases in vector-borne diseases. "
            "Climate change has reduced food and water security, hindering efforts to "
            "meet Sustainable Development Goals. The health co-benefits of ambitious "
            "mitigation action are estimated to be worth two to three times the cost "
            "of mitigation measures."
        ),
    },
    {
        "title": "AR6 SPM: Equity and Justice",
        "content": (
            "The countries that have contributed least to global warming are often those "
            "most vulnerable to climate change impacts. Historical cumulative CO2 emissions "
            "are strongly correlated with current wealth. Addressing inequality and "
            "providing climate finance and technology transfer to developing countries "
            "are essential components of a just and effective global climate response."
        ),
    },
    {
        "title": "AR6 SPM: Tipping Points",
        "content": (
            "Climate tipping points occur when a small change in forcing triggers a larger "
            "change in the Earth system. Examples include the collapse of the West Antarctic "
            "Ice Sheet, dieback of the Amazon rainforest, and permafrost thaw releasing "
            "stored carbon. Beyond 1.5°C, the risk of crossing tipping points increases "
            "significantly, potentially triggering cascading effects across Earth systems."
        ),
    },
]

# NDC (Nationally Determined Contribution) summaries — country-specific
NDC_SUMMARIES = [
    {
        "iso_code": "US",
        "title": "United States NDC 2021",
        "content": (
            "The United States has set a target of reducing greenhouse gas emissions "
            "50–52% below 2005 levels by 2030. This target covers all greenhouse gases "
            "and all economic sectors. Key measures include transitioning to clean "
            "electricity, electrifying transportation and buildings, and reducing methane "
            "from the oil and gas sector. The US aims to reach net-zero greenhouse gas "
            "emissions by no later than 2050."
        ),
        "url": "https://www4.unfccc.int/sites/ndcstaging/PublishedDocuments/United%20States%20of%20America%20First/United%20States%20NDC%20April%2021%202021%20Final.pdf",
    },
    {
        "iso_code": "CN",
        "title": "China NDC 2021",
        "content": (
            "China aims to peak CO2 emissions before 2030 and achieve carbon neutrality "
            "before 2060. Specific targets include lowering CO2 intensity of GDP by over "
            "65% from the 2005 level by 2030, increasing the share of non-fossil fuels in "
            "primary energy consumption to around 25% by 2030, and increasing forest stock "
            "volume by 6 billion cubic meters from the 2005 level. China plans to bring "
            "its wind and solar power capacity to over 1,200 GW by 2030."
        ),
        "url": "https://unfccc.int/sites/default/files/NDC/2022-06/China%27s%20Updated%20Nationally%20Determined%20Contribution.pdf",
    },
    {
        "iso_code": "IN",
        "title": "India NDC 2022",
        "content": (
            "India's updated NDC targets include reducing the emissions intensity of GDP "
            "by 45% by 2030, compared to the 2005 level, and achieving about 50% cumulative "
            "electric power installed capacity from non-fossil fuel-based energy resources "
            "by 2030. India also aims to create an additional carbon sink of 2.5 to 3 "
            "billion tonnes of CO2 equivalent through additional forest and tree cover by "
            "2030. India's long-term goal is net zero by 2070."
        ),
        "url": "https://unfccc.int/sites/default/files/NDC/2022-08/India%20Updated%20First%20Nationally%20Determined%20Contribution%202021-2030.pdf",
    },
    {
        "iso_code": "GB",
        "title": "United Kingdom NDC 2020",
        "content": (
            "The UK's NDC commits to reducing economy-wide greenhouse gas emissions by "
            "at least 68% by 2030, compared to 1990 levels. The UK was the first major "
            "economy to legislate for net zero emissions by 2050. Key sectors include "
            "power generation (targeting zero-carbon electricity by 2035), transport "
            "(ending new petrol/diesel car sales by 2030), buildings (improving energy "
            "efficiency and low-carbon heat), and industry."
        ),
    },
    {
        "iso_code": "BR",
        "title": "Brazil NDC 2022",
        "content": (
            "Brazil's updated NDC commits to reducing greenhouse gas emissions by 50% "
            "by 2030 compared to 2005 levels. Key commitments include eliminating illegal "
            "deforestation by 2030, restoring 12 million hectares of forests, and achieving "
            "a 45–50% share of renewables in its total energy mix. Brazil aims to reach "
            "climate neutrality by 2050. Agriculture and land-use change are central to "
            "Brazil's climate challenge, as they account for the majority of its emissions."
        ),
    },
    {
        "iso_code": "AU",
        "title": "Australia NDC 2022",
        "content": (
            "Australia updated its NDC to commit to a 43% reduction in emissions below "
            "2005 levels by 2030 and net zero emissions by 2050. The updated target "
            "reflects a significant increase from the previous 26–28% target. Australia "
            "plans to invest in renewable energy, hydrogen, and electric vehicles. "
            "Australia's per capita emissions are among the highest in the OECD, largely "
            "due to its coal-heavy energy mix and resource extraction industries."
        ),
    },
    {
        "iso_code": "DE",
        "title": "Germany NDC (EU) 2020",
        "content": (
            "Germany contributes to the EU NDC, which commits the European Union to "
            "reducing net greenhouse gas emissions by at least 55% by 2030 compared to "
            "1990 levels, and reaching climate neutrality by 2050. Germany's national "
            "Climate Action Programme targets a 65% reduction by 2030 vs 1990 and net "
            "zero by 2045—five years ahead of the EU target. Germany's Energiewende "
            "policy drives a rapid transition away from coal and nuclear to renewables."
        ),
    },
    {
        "iso_code": "FR",
        "title": "France NDC (EU) 2020",
        "content": (
            "France, as an EU member, commits to the EU NDC target of at least 55% "
            "greenhouse gas reduction by 2030 versus 1990. France's national carbon "
            "neutrality law targets net-zero emissions by 2050. France's low-carbon "
            "strategy relies heavily on nuclear power (70% of electricity generation) "
            "and rapid expansion of renewables. Key sectors for decarbonisation include "
            "transport, buildings, and agriculture."
        ),
    },
    {
        "iso_code": "JP",
        "title": "Japan NDC 2021",
        "content": (
            "Japan's updated NDC targets a 46% reduction in greenhouse gas emissions "
            "by fiscal year 2030 compared to fiscal year 2013, striving for a 50% "
            "reduction. Japan aims to achieve carbon neutrality by 2050. Key strategies "
            "include expanding renewables to 36–38% of electricity by 2030, hydrogen "
            "energy deployment, reducing energy consumption, and developing next-generation "
            "nuclear power. Japan's industrial sector is central to its decarbonisation "
            "challenge."
        ),
    },
    {
        "iso_code": "CA",
        "title": "Canada NDC 2021",
        "content": (
            "Canada's updated NDC commits to reducing greenhouse gas emissions by "
            "40–45% below 2005 levels by 2030 and achieving net-zero emissions by 2050. "
            "Canada's climate plan includes a national carbon price rising to CA$170/tonne "
            "by 2030, clean electricity regulations, and methane reduction from oil and "
            "gas. Canada's high emissions are driven by its oil sands, transportation, "
            "and energy-intensive industries."
        ),
    },
]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    """Split text at sentence boundaries keeping each chunk under max_chars."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sent in sentences:
        if current and current_len + len(sent) + 1 > max_chars:
            chunks.append(" ".join(current))
            current = [sent]
            current_len = len(sent)
        else:
            current.append(sent)
            current_len += len(sent) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def get_country_id(db: Session, iso_code: str) -> Optional[int]:
    from app.models.country import Country
    row = db.query(Country.id).filter(Country.iso_code == iso_code).first()
    return row[0] if row else None


def seed(db: Session, model: SentenceTransformer) -> None:
    existing_types = {r[0] for r in db.query(SourceDocument.source_type).distinct().all()}

    docs_to_embed: list[DocumentChunk] = []

    # --- IPCC AR6 ---
    if "ipcc_ar6" not in existing_types:
        print("Seeding IPCC AR6 findings…")
        for item in IPCC_AR6_FINDINGS:
            source_doc = SourceDocument(
                source_type="ipcc_ar6",
                title=item["title"],
                full_content=item["content"],
                country_id=None,
                url=item.get("url"),
            )
            db.add(source_doc)
            db.flush()  # get source_doc.id
            for idx, chunk_text_str in enumerate(chunk_text(item["content"])):
                chunk = DocumentChunk(
                    source_doc_id=source_doc.id,
                    chunk_index=idx,
                    content=chunk_text_str,
                )
                db.add(chunk)
                docs_to_embed.append(chunk)
        db.flush()
    else:
        print("IPCC AR6 already seeded — skipping.")

    # --- NDCs ---
    if "ndc" not in existing_types:
        print("Seeding NDC summaries…")
        for item in NDC_SUMMARIES:
            country_id = get_country_id(db, item["iso_code"])
            source_doc = SourceDocument(
                source_type="ndc",
                title=item["title"],
                full_content=item["content"],
                country_id=country_id,
                url=item.get("url"),
            )
            db.add(source_doc)
            db.flush()
            for idx, chunk_text_str in enumerate(chunk_text(item["content"])):
                chunk = DocumentChunk(
                    source_doc_id=source_doc.id,
                    chunk_index=idx,
                    content=chunk_text_str,
                )
                db.add(chunk)
                docs_to_embed.append(chunk)
        db.flush()
    else:
        print("NDC summaries already seeded — skipping.")

    if not docs_to_embed:
        print("Nothing new to embed.")
        db.commit()
        return

    print(f"Embedding {len(docs_to_embed)} chunks…")
    texts = [c.content for c in docs_to_embed]
    vectors = model.encode(texts, batch_size=64, show_progress_bar=True)
    for chunk, vec in zip(docs_to_embed, vectors):
        chunk.embedding = vec.tolist()

    db.commit()
    print(f"Done. Seeded {len(docs_to_embed)} chunks.")


def main() -> None:
    print("Loading embedding model…")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    db: Session = SessionLocal()
    try:
        seed(db, model)
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
