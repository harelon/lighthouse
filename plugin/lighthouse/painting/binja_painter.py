import logging

import binaryninja
from binaryninja import HighlightStandardColor
from binaryninja.highlight import HighlightColor

from lighthouse.painting import DatabasePainter
from lighthouse.util.disassembler import disassembler

logger = logging.getLogger("Lighthouse.Painting.Binja")

#------------------------------------------------------------------------------
# Binary Ninja Painter
#------------------------------------------------------------------------------

class BinjaPainter(DatabasePainter):
    """
    Asynchronous Binary Ninja database painter.
    """
    PAINTER_SLEEP = 0.01

    def __init__(self, lctx, director, palette):
        super(BinjaPainter, self).__init__(lctx, director, palette)

    #--------------------------------------------------------------------------
    # Paint Primitives
    #--------------------------------------------------------------------------

    #
    # NOTE:
    #   due to the manner in which Binary Ninja implements basic block
    #   (node) highlighting, I am not sure it is worth it to paint individual
    #   instructions. for now we, will simply make the instruction
    #   painting functions no-op's
    #

    def _paint_instructions(self, instructions):
        self._action_complete.set()

    def _clear_instructions(self, instructions):
        self._action_complete.set()

    def _paint_nodes(self, nodes_coverage):
        bv = disassembler[self.lctx].bv
        r, g, b, _ = self.palette.coverage_paint.getRgb()
        color = HighlightColor(red=r, green=g, blue=b)
        for node_coverage in nodes_coverage:
            node_metadata = node_coverage.database._metadata.nodes[node_coverage.address]
            for node in bv.get_basic_blocks_starting_at(node_metadata.address):
                node.highlight = color
            self._painted_nodes.add(node_metadata.address)
        self._action_complete.set()

    def _clear_nodes(self, nodes_metadata):
        bv = disassembler[self.lctx].bv
        for node_metadata in nodes_metadata:
            for node in bv.get_basic_blocks_starting_at(node_metadata.address):
                node.highlight = HighlightStandardColor.NoHighlightColor
            self._painted_nodes.discard(node_metadata.address)
        self._action_complete.set()

    def _refresh_ui(self):
        pass

    def _cancel_action(self, job):
        pass

    #--------------------------------------------------------------------------
    # Priority Painting
    #--------------------------------------------------------------------------

    def _priority_paint(self):
        disassembler_ctx = disassembler[self.lctx]
        db_metadata = self.director.metadata
        return True # TODO

        current_address = disassembler_ctx.get_current_address()
        current_function = disassembler.bv.get_function_at(current_address)
        function_metadata = db_metadata.get_closest_function(current_address)

        if current_function and function_metadata:
            self._paint_function(current_function.start)

        return True

