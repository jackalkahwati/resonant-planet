"""
PDF report generation for detection runs.
"""
import io
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

logger = logging.getLogger(__name__)


def generate_pdf_report(
    job_id: str,
    candidates: List[Dict],
    dataset_name: str,
    output_path: str,
    method_summary: Optional[str] = None,
) -> str:
    """
    Generate PDF report for a detection run.

    Parameters
    ----------
    job_id : str
        Job identifier
    candidates : List[Dict]
        List of candidate dictionaries
    dataset_name : str
        Name of the dataset
    output_path : str
        Output PDF path
    method_summary : str, optional
        Summary of methods used

    Returns
    -------
    str
        Path to generated PDF
    """
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []

    # Get styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
    )

    # Title
    story.append(Paragraph("Resonant Worlds Explorer", title_style))
    story.append(Paragraph("Exoplanet Detection Report", styles["Heading2"]))
    story.append(Spacer(1, 0.3 * inch))

    # Metadata
    metadata = [
        ["Job ID:", job_id],
        ["Dataset:", dataset_name],
        ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Total Candidates:", str(len(candidates))],
    ]

    metadata_table = Table(metadata, colWidths=[2 * inch, 4 * inch])
    metadata_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(metadata_table)
    story.append(Spacer(1, 0.4 * inch))

    # Method summary
    if method_summary:
        story.append(Paragraph("Methods", heading_style))
        story.append(Paragraph(method_summary, body_style))
        story.append(Spacer(1, 0.3 * inch))
    else:
        default_summary = """
        This report presents exoplanet candidates detected using the Resonant Worlds Explorer pipeline.
        The pipeline combines Box Least Squares (BLS) period search, physics-informed transit modeling
        via local Modulus code, Qwen Omni time series embeddings, and reinforcement learning-based triage.
        Each candidate has been validated using odd-even transit tests, secondary eclipse searches,
        and stellar density consistency checks.
        """
        story.append(Paragraph("Methods", heading_style))
        story.append(Paragraph(default_summary.strip(), body_style))
        story.append(Spacer(1, 0.3 * inch))

    # Summary statistics
    accepted = sum(1 for c in candidates if c.get("rl_action") == "accept")
    rejected = sum(1 for c in candidates if c.get("rl_action") == "reject")
    review = sum(1 for c in candidates if c.get("rl_action") == "human_review")

    story.append(Paragraph("Detection Summary", heading_style))

    summary_data = [
        ["Status", "Count", "Percentage"],
        ["Accepted", str(accepted), f"{100 * accepted / len(candidates):.1f}%"],
        ["Rejected", str(rejected), f"{100 * rejected / len(candidates):.1f}%"],
        ["Human Review", str(review), f"{100 * review / len(candidates):.1f}%"],
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 0.4 * inch))

    # Top candidates
    story.append(Paragraph("Top Candidates", heading_style))

    for i, candidate in enumerate(candidates[:5], 1):
        story.append(Paragraph(f"Candidate {i}: {candidate['candidate_id']}", styles["Heading3"]))

        # Candidate details
        details = [
            ["Parameter", "Value"],
            ["Probability", f"{candidate['probability']:.3f}"],
            ["Period", f"{candidate['period_days']:.4f} days"],
            ["Epoch (BJD)", f"{candidate['t0_bjd']:.4f}"],
            ["Depth", f"{candidate['depth_ppm']:.1f} ppm"],
            ["Duration", f"{candidate['duration_hours']:.2f} hours"],
            ["SNR", f"{candidate['snr']:.1f}"],
            ["RL Action", candidate['rl_action'].replace("_", " ").title()],
        ]

        details_table = Table(details, colWidths=[2 * inch, 2.5 * inch])
        details_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
                ]
            )
        )

        story.append(details_table)
        story.append(Spacer(1, 0.2 * inch))

        # Add plots if available
        plots = candidate.get("plots", {})

        if plots.get("phase_fold_png") and Path(plots["phase_fold_png"]).exists():
            try:
                img = Image(plots["phase_fold_png"], width=5 * inch, height=3 * inch)
                story.append(img)
                story.append(Spacer(1, 0.1 * inch))
            except Exception as e:
                logger.warning(f"Could not add phase fold plot: {e}")

        # Page break between candidates
        if i < min(5, len(candidates)):
            story.append(PageBreak())

    # Build PDF
    doc.build(story)

    logger.info(f"Generated PDF report: {output_path}")
    return output_path


def generate_comparison_report(
    candidate_id: str,
    baseline_metrics: Dict,
    resonant_metrics: Dict,
    output_path: str,
) -> str:
    """
    Generate comparison report for baseline vs resonant methods.

    Parameters
    ----------
    candidate_id : str
        Candidate identifier
    baseline_metrics : Dict
        Baseline method metrics
    resonant_metrics : Dict
        Resonant method metrics
    output_path : str
        Output PDF path

    Returns
    -------
    str
        Path to generated PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph("Method Comparison Report", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    # Candidate info
    story.append(Paragraph(f"Candidate: {candidate_id}", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    # Comparison table
    comparison_data = [
        ["Metric", "Baseline", "Resonant", "Improvement"],
        [
            "Detection Probability",
            f"{baseline_metrics['detection_probability']:.3f}",
            f"{resonant_metrics['detection_probability']:.3f}",
            f"{100 * (resonant_metrics['detection_probability'] - baseline_metrics['detection_probability']) / baseline_metrics['detection_probability']:.1f}%",
        ],
        [
            "SNR",
            f"{baseline_metrics['snr']:.2f}",
            f"{resonant_metrics['snr']:.2f}",
            f"{100 * (resonant_metrics['snr'] - baseline_metrics['snr']) / baseline_metrics['snr']:.1f}%",
        ],
        [
            "False Alarm Rate",
            f"{baseline_metrics['false_alarm_rate']:.4f}",
            f"{resonant_metrics['false_alarm_rate']:.4f}",
            f"{100 * (baseline_metrics['false_alarm_rate'] - resonant_metrics['false_alarm_rate']) / baseline_metrics['false_alarm_rate']:.1f}%",
        ],
        [
            "Compute Time (s)",
            f"{baseline_metrics['compute_time_seconds']:.2f}",
            f"{resonant_metrics['compute_time_seconds']:.2f}",
            f"{100 * (baseline_metrics['compute_time_seconds'] - resonant_metrics['compute_time_seconds']) / baseline_metrics['compute_time_seconds']:.1f}%",
        ],
    ]

    comparison_table = Table(comparison_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    comparison_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#95a5a6")),
            ]
        )
    )

    story.append(comparison_table)

    # Build PDF
    doc.build(story)

    logger.info(f"Generated comparison report: {output_path}")
    return output_path
