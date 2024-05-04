import yaml
from copy import deepcopy

from .cells import Cell, CodeCell, DocCell, CellsStream, Vars, Attrs, RunContext
from .tags import parse_tags
from .files import Files
from .input import RawDocument, is_vdf
from .document import Document, Episode
from .literals import *
from .tags import TAG_DEFS
from ..helpers import *


class VdfProcessor:
    """
    Handles VDF magic
    """
    # TODO: init section with defines to processor (if necessary)

    @critical_todo
    def process_cell(
        self,
        document    : Document,
        cell        : Cell,
    ) -> tuple[Document, Cell]:
        """
        Process cell depending on it's content and current document state
        """
        # What to do:
        # 1. Take current state of document
        # 2. Take cell
        # 3. Detect tags in cell
        #  - depends on whether it's code or doc cell
        #  - make sure every tag is enabled
        #  - also determine fallback language for cell content
        # 4. Determine
        #  - cell name and check it's unique
        #  - parent stage/cell
        # 5. Get context
        # 6. Make temporary altered context by side tags
        #   (alter attrs and vars)
        # 7. Process cell according to context and tags
        #   - convert data if there is #convert tag
        # 8. Update produced files
        # 9. Put result into branch / flow

        # Implementation:

        # 0. it's possible that cell is in a raw text form
        # (this would be the case if called by Jupyter's magic)
        # If so - convert text into ad-hoc cell
        if isinstance(cell, tuple):
            cell = RawDocument.parse_code_content(*cell)


        # 1. Take current state of document

        # Output document
        d = document.clone()

        # Temporary document with ad-hoc changes for cell run
        # (vars / attrs may be temporary altered with cell's tags)
        d_tmp = document.clone()

        # Remove document from scope to avoid harming it by accident
        _orig_document = document
        del document

        # 2. Take cell

        # Make sure cell wasn't processed yet
        if cell.input_context is not None \
        or cell.output_context is not None \
        or cell.tags is not None \
        :
            raise ValueError("Cell is already processed!")

        # Get cell's lines in simple and linear form
        raw_lines = [v.replace("\n", "") for v in cell.raw_lines()]

        # 3. Determine tags, extract first-order tags (name, branch, fork, parent, flow)
        is_vdf_cell = None
        cell_name = None
        def_lang = None

        if isinstance(cell, CodeCell):
            is_vdf_cell = is_vdf(cell.content[0].kind, raw_lines)
            if is_vdf_cell:
                def_lang = cell.content[0].kind
                if def_lang == S_VDF:
                    def_lang = None
                if def_lang is not None and def_lang[-1-len(S_VDF)] == "-"+S_VDF:
                    def_lang = def_lang[:-1-len(S_VDF)]
                if def_lang is not None and def_lang == "":
                    def_lang = None
                tags, t_name, t_parent = parse_tags(raw_lines[1:])
                # NOTE: tags may span across multiple lines if lines are ending with \
                # and "lines merging" is not natively supported by input format
            else:
                # TODO: look for tags in first non-empty line
                # (may appear after commenting sequence)
                raise NotImplementedError(
                    "Code cells except VDF cells aren't supported yet!")
                tags, t_name, t_parent = [None]*3
        else:
            pass # TODO: look for tags in first non-empty line
            # TODO: if there were tags - remove line with tags from output
            # NOTE: tags may be span across multiple lines if line ends with \
            # and "lines merging" is not natively supported by input format
            # So in this case need to remove multiple lines from output
            tags, t_name, t_parent = [None]*3

        # TODO: make sure that all tags are allowed / defined

        # 4. Determine cell's name, parent cell

        ## Cell Name
        cell_name = t_name or cell.name

        # Check that name is unique
        if cell_name in d.named_episodes():
            raise ValueError(f"Cell name '{cell_name}' were already taken!")

        # Lookup parent if there is any
        if t_parent is not None:
            parent = d.lookup_episode_by_cell_name(t_parent)
            if parent is None:
                raise ValueError(f"Parent cell with name '{t_parent}' was not found!")
            else:
                parent = parent['episode']
        else:
            default_branch_name = d.default_branch
            # TODO: check if there is branch attr already set / would be set by tag
            # parent could be
            # - last stage in default branch
            # - last stage in specified branch
            # - root of document for new branch without parent
            parent = d.last_episode_in_branch(default_branch_name, not_exist_ok=True)

        # Apply tags (step 5,6,7)

        # Remove cell from scope to avoid harming it by accident
        _orig_cell = cell
        del cell

        # Init cell and apply tags
        if parent is None:
            context = d.root_context
        elif parent.cell is None:
            context = parent.entry_context
        else:
            context = parent.cell.output_context

        cell_context = deepcopy(context)

        # Prepare cell for processing
        # - inherit source info from input cell
        # - set context for
        cell_type = (DocCell, CodeCell)[isinstance(_orig_cell, CodeCell)]
        # TODO: probably there is a better way to get class for new output_cell
        output_cell = cell_type(
            _orig_cell.content,
            _orig_cell.location,
            cell_context,
            tags,
            cell_name,
        )

        # Apply tags at last
        self.apply_tags(d, output_cell, def_lang)

        new_episode = Episode(context, _orig_cell.location, output_cell)

        branch_name = "__main__"    # TODO: get from output_cell? applied_tags?

        # 8. # TODO: Update produced files
        # (in output_cell.context)

        # 9. Put result into branch / flow
        # (in d)
        # a stub for now
        d.ensure_branch(branch_name, parent)
        d.branches.by_name(branch_name).append(new_episode)
        # TODO: Put result into flows

        return d, output_cell


    @stub_alert
    def apply_tags(self, document:Document, cell:Cell, def_lang:str) -> bool:
        # Apply tags in following order
        #  1. set vars (temporary)
        #  2. check conditions
        #  3. subst cell's content with vars
        #  4. get cell's data from external sources
        #  5. set target file / subsection
        #  6. convert cell content
        #  7. set other attributes  # TODO: determine when better do this
        #  8. other pre-processing tags
        #  9. apply main tag (in some cases there can be no main tag)
        # 10. other post-processing tags
        # 12. show/output (common action, not a tag)

        # Determine output file name
        # Depends on
        #   - subject
        #   - lang
        #   - kind
        #   - target

        # If default code file were defined already
        # (implicitly by the first #code tag)
        # make sure subject and/or kind or target
        # is defined for code tags with other lang
        return True

    @critical_todo
    def initialize_doc(
        self,
        document    : Document
    ) -> Document:
        """
        Initialize documents context
        """
        # Don't touch original document - always add a layer
        _orig = document
        document = Document(_orig.source, _orig.frontmatter, _orig.root_context)

        root_context = document.root_context

        # Run through all tags and set default attrs
        for _,v in TAG_DEFS.tags.items():
            defaults = v.runner.defaults()
            if defaults is not None:
                for kk,vv in defaults:
                    if kk in root_context.attrs.data:
                        raise ValueError(f"Attribute '{kk}' were already defined by previous tag!")
                root_context.attrs.data[kk] = vv
            # TODO: define defaults for tags like
            # - fetch
            # - and so...

        # Update attrs / vars
        if document.frontmatter is not None:
            frontmatter_raw = "".join(document.frontmatter.raw_lines()).encode()
            frontmatter = yaml.safe_load(frontmatter_raw)
            if S_VARS in frontmatter:
                for k,v in frontmatter[S_VARS].items():
                    root_context.vars.data[k] = v
            if S_ATTRS in frontmatter:
                for k,v in frontmatter[S_ATTRS].items():
                    root_context.attrs.data[k] = v
            if S_DEFINE in frontmatter:
                for tag in frontmatter[S_DEFINE]:
                    # TODO: construct tag and invoke apply
                    raise NotImplementedError("Not implemented yet!")
            if S_VER in frontmatter:
                root_context.vdf_ver = frontmatter[S_VER]

        return document

    def process_doc(
        self,
        document    : Document
    ):
        """
        Initialize document's context and process all source cells
        """
        d = self.initialize_doc(document)

        # Remove document from scope to avoid harming it by accident
        _orig_document = document
        del document

        stages = [(d,None,None)]
        for cell in d.source.cells:
            d, c = self.process_cell(d, cell)
            stages.append((d, cell.location, c))
        return stages
