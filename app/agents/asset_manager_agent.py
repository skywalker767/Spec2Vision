"""Asset generation and persistence agent."""

from __future__ import annotations

from pathlib import Path

from app.models.schemas import WorkflowState
from app.tools.asset_store import save_json, save_text
from app.tools.diagram_generator import DiagramGenerator
from app.tools.image_factory import get_image_generator
from app.tools.trace_logger import TraceLogger
from app.tools.trace_logger import append_trace


class AssetManagerAgent:
    """Generate visual assets and persist all outputs."""

    def __init__(self):
        self.image_gen = get_image_generator()
        self.diagram_gen = DiagramGenerator()

    def generate_asset(self, state: WorkflowState) -> WorkflowState:
        """Call Image or Diagram tool based on task_type."""
        if not state.visual_spec:
            raise ValueError("VisualSpec required for asset generation")

        vs = state.visual_spec
        title = vs.title

        if state.task_type == "academic_figure":
            # Respect requested output format from VisualSpec.
            # - svg: generate deterministic SVG flowchart locally
            # - png: generate raster image via image API (prompt must be an image prompt)
            fmt = (vs.output_format or "").lower().strip()
            if fmt == "png":
                path = self.image_gen.generate(
                    state.task_id,
                    state.task_type,
                    title,
                    state.prompt,
                    aspect_ratio=vs.aspect_ratio,
                )
            else:
                # svg / mermaid treated as SVG for the rendered asset
                path = self.diagram_gen.generate(state.task_id, vs)
        else:
            path = self.image_gen.generate(
                state.task_id,
                state.task_type,
                title,
                state.prompt,
                aspect_ratio=vs.aspect_ratio,
            )

        state.output_path = str(path)
        append_trace(
            state.traces,
            agent_name="AssetManagerAgent",
            step="generate_asset",
            input_summary=state.task_type,
            output_summary=str(path.name),
            metadata={
                "output_path": str(path),
                "image_provider": "openai",
            },
        )
        return state

    def save_assets(self, state: WorkflowState) -> WorkflowState:
        """Save prompt, evaluation report, and trace to storage."""
        task_id = state.task_id

        prompt_path = save_text(task_id, "prompt", "prompt.txt", state.prompt)
        report_data = state.evaluation.model_dump() if state.evaluation else {}
        report_path = save_json(task_id, "report", "evaluation.json", report_data)

        logger = TraceLogger(state.traces)
        trace_path = logger.save(task_id)

        state.report_path = str(report_path)
        append_trace(
            state.traces,
            agent_name="AssetManagerAgent",
            step="save_assets",
            input_summary=task_id,
            output_summary=f"prompt={prompt_path.name}, report={report_path.name}",
            metadata={
                "prompt_path": str(prompt_path),
                "report_path": str(report_path),
                "trace_path": str(trace_path),
                "output_path": state.output_path,
            },
        )
        return state
