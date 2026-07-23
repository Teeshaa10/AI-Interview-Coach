import { jsPDF } from "jspdf";

import type { InterviewReport } from "@/types/report";
import { formatDateTime } from "@/utils/format";

const PAGE_WIDTH = 210;
const PAGE_HEIGHT = 297;
const MARGIN = 18;
const CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2;

class PdfCursor {
  doc: jsPDF;
  y: number;

  constructor(doc: jsPDF) {
    this.doc = doc;
    this.y = MARGIN;
  }

  ensureSpace(height: number) {
    if (this.y + height > PAGE_HEIGHT - MARGIN) {
      this.doc.addPage();
      this.y = MARGIN;
    }
  }

  heading(text: string) {
    this.ensureSpace(12);
    this.doc.setFont("helvetica", "bold");
    this.doc.setFontSize(14);
    this.doc.setTextColor(30, 41, 59);
    this.doc.text(text, MARGIN, this.y);
    this.y += 8;
  }

  subheading(text: string) {
    this.ensureSpace(8);
    this.doc.setFont("helvetica", "bold");
    this.doc.setFontSize(11);
    this.doc.setTextColor(51, 65, 85);
    this.doc.text(text, MARGIN, this.y);
    this.y += 6;
  }

  paragraph(text: string) {
    if (!text) return;
    this.doc.setFont("helvetica", "normal");
    this.doc.setFontSize(10);
    this.doc.setTextColor(71, 85, 105);
    const lines: string[] = this.doc.splitTextToSize(text, CONTENT_WIDTH);
    for (const line of lines) {
      this.ensureSpace(5.5);
      this.doc.text(line, MARGIN, this.y);
      this.y += 5.5;
    }
  }

  bulletList(items: string[]) {
    this.doc.setFont("helvetica", "normal");
    this.doc.setFontSize(10);
    this.doc.setTextColor(71, 85, 105);
    for (const item of items) {
      const lines: string[] = this.doc.splitTextToSize(`\u2022 ${item}`, CONTENT_WIDTH - 4);
      for (const [index, line] of lines.entries()) {
        this.ensureSpace(5.5);
        this.doc.text(line, MARGIN + (index === 0 ? 0 : 4), this.y);
        this.y += 5.5;
      }
    }
  }

  divider() {
    this.ensureSpace(6);
    this.doc.setDrawColor(226, 232, 240);
    this.doc.line(MARGIN, this.y, PAGE_WIDTH - MARGIN, this.y);
    this.y += 6;
  }

  spacer(amount = 4) {
    this.y += amount;
  }
}

function scoreLine(cursor: PdfCursor, label: string, value: number) {
  cursor.ensureSpace(6);
  cursor.doc.setFont("helvetica", "normal");
  cursor.doc.setFontSize(10);
  cursor.doc.setTextColor(71, 85, 105);
  cursor.doc.text(label, MARGIN, cursor.y);
  cursor.doc.setFont("helvetica", "bold");
  cursor.doc.setTextColor(30, 41, 59);
  cursor.doc.text(value.toFixed(1), PAGE_WIDTH - MARGIN, cursor.y, { align: "right" });
  cursor.y += 6;
}

/**
 * Builds and downloads a PDF summary of an interview report entirely in
 * the browser (no server round-trip), using the same data already shown
 * on the report detail page.
 */
export function exportReportToPdf(report: InterviewReport): void {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const cursor = new PdfCursor(doc);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(15, 23, 42);
  doc.text("Interview Report", MARGIN, cursor.y);
  cursor.y += 9;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(100, 116, 139);
  doc.text(`${report.job_role} \u2022 ${report.experience_level}`, MARGIN, cursor.y);
  cursor.y += 5;
  if (report.interview_completed_at) {
    doc.text(`Completed ${formatDateTime(report.interview_completed_at)}`, MARGIN, cursor.y);
    cursor.y += 5;
  }
  cursor.spacer(2);
  cursor.divider();

  cursor.heading("Scores");
  scoreLine(cursor, "Overall score", report.overall_score);
  scoreLine(cursor, "Technical", report.technical_score);
  scoreLine(cursor, "Communication", report.communication_score);
  scoreLine(cursor, "Completeness", report.completeness_score);
  cursor.spacer(2);
  cursor.paragraph(
    `${report.answered_questions} of ${report.total_questions} questions answered (${report.completion_percentage.toFixed(0)}% complete). Recommended next difficulty: ${report.recommended_next_difficulty}.`,
  );
  cursor.spacer(2);
  cursor.divider();

  if (report.summary) {
    cursor.heading("Summary");
    cursor.paragraph(report.summary);
    cursor.spacer(2);
    cursor.divider();
  }

  if (report.strengths.length > 0) {
    cursor.subheading("Strengths");
    cursor.bulletList(report.strengths);
    cursor.spacer(2);
  }

  if (report.weaknesses.length > 0) {
    cursor.subheading("Weaknesses");
    cursor.bulletList(report.weaknesses);
    cursor.spacer(2);
  }

  if (report.improvement_plan.length > 0) {
    cursor.subheading("Improvement Plan");
    cursor.bulletList(report.improvement_plan);
    cursor.spacer(2);
  }

  if (report.question_breakdown.length > 0) {
    cursor.divider();
    cursor.heading("Question Breakdown");
    for (const item of report.question_breakdown) {
      cursor.ensureSpace(10);
      cursor.subheading(`Q${item.question_number}. ${item.question}`);
      cursor.doc.setFont("helvetica", "italic");
      cursor.doc.setFontSize(9);
      cursor.doc.setTextColor(100, 116, 139);
      cursor.ensureSpace(5);
      cursor.doc.text(
        `${item.category}${item.overall_score !== null ? ` \u2022 Score: ${item.overall_score.toFixed(1)}` : ""}`,
        MARGIN,
        cursor.y,
      );
      cursor.y += 5.5;

      if (item.answer) {
        cursor.paragraph(`Answer: ${item.answer}`);
      }
      if (item.feedback) {
        cursor.paragraph(`Feedback: ${item.feedback}`);
      }
      cursor.spacer(3);
    }
  }

  const pageCount = doc.getNumberOfPages();
  for (let page = 1; page <= pageCount; page += 1) {
    doc.setPage(page);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(148, 163, 184);
    doc.text(`Page ${page} of ${pageCount}`, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 10, { align: "right" });
    doc.text("AI Interview Coach", MARGIN, PAGE_HEIGHT - 10);
  }

  const safeRole = report.job_role.trim().replace(/[^a-z0-9]+/gi, "-").toLowerCase() || "interview";
  doc.save(`report-${safeRole}-${report.interview_id.slice(0, 8)}.pdf`);
}
