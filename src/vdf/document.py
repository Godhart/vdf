# Classes for handling large VDF structures
from copy import deepcopy
from .cells import Cell, CellsStream, Vars, Attrs, RunContext
from .files import Files
from ..helpers import *


class Episode:
    """
    Episode data storage
    """
    def __init__(
            self,
            entry_context: RunContext,
            source_cell_location: list,
            cell: Cell,
    ):
        # Context on stage entry
        self.entry_context = entry_context

        # Path to the source for cell
        self.source_cell_location = source_cell_location

        # Cell that were produced on this stage
        self.cell = cell


class Arc:
    """
    Storage for series of episodes
    """
    def __init__(
            self,
            episodes: list[Episode],
    ):
        self.episodes = episodes


class Story:
    """
    Contains story data and methods to work with it
    """
    def __init__(self, arc:Arc, parent:Episode):
        self.arc = arc  # Contains context for each episode in story
        self.parent = parent

    @property
    def last_episode(self) -> (Episode|None):
        if len(self.arc.episodes) > 0:
            return self.arc.episodes[-1]
        else:
            return None

    def append(self, episode:Episode):
        self.arc.episodes.append(episode)


class Stories:
    """
    Multiple stories storage
    """
    def __init__(self, data:dict[str:Story]):
        self.data = data

    def by_name(self, name) -> (Story|None):
        return self.data.get(name, None)


class Document:
    """
    Class for whole document **state** representation
    Contains all it's history, branches, flows etc. at current point
    """
    def __init__(self, source:CellsStream, frontmatter:Cell|None, root_context:None):
        self._frontmatter = frontmatter # Frontmatter part
        self._source = source           # Document's source cell's (cells that are not processed)
        self._branches = Stories({})    # Registered cell's branches
        self._flows = Stories({})       # Registered production flows
        self._root_context = root_context or RunContext(
            CellsStream([]),
            Files([]),
            CellsStream([]),
            Vars({}),
            Attrs({}),
            "1.0"
        )
        self._default_branch = "__main__"

    @property
    def frontmatter(self):
        return self._frontmatter

    @property
    def source(self):
        return self._source

    @property
    def branches(self):
        return self._branches

    @property
    def flows(self):
        return self._flows

    @property
    def root_context(self):
        return self._root_context

    @property
    def default_branch(self):
        return self._default_branch

    @critical_todo
    def clone(self):
        """
        Properly clone self to save space but preserve references
        """
        result = Document(self._source, self._frontmatter, self._root_context)
        # TODO: will it save refs to source from cells?
        result._branches = deepcopy(self._branches)
        result._flows = deepcopy(self._flows)
        result._default_branch = self._default_branch
        return result

    def named_episodes(self) -> dict[str:Cell]:
        """
        Get all episodes with named cells
        Key is cell name
        Value is a dict with:
        - branch_name
        - episode idx in branch
        - episode ref
        """
        result = {}
        for k,v in self.branches.data.items():
            i = -1
            for ep in v.arc.episodes:
                i += 1
                if ep.cell.name[:1] != "_":
                    result[ep.cell.name] = {
                        "branch"        : k,
                        "episode_idx"   : i,
                        "episode"       : ep,
                    }
        return result

    def lookup_episode_by_cell_name(self, cell_name:str) -> dict|None:
        """
        Lookup stage by cell name
        None returned if not found
        Return dict with:
        - branch_name
        - episode idx in branch
        - episode ref
        """
        for k,v in self.branches.data.items():
            i = -1
            for ep in v.arc.episodes:
                i += 1
                if ep.cell.name == cell_name:
                    result = {
                        "branch"        : k,
                        "episode_idx"   : i,
                        "episode"       : ep,
                    }
                    return result
        return None

    def last_episode_in_branch(self, branch_name:str, not_exist_ok:bool=False) -> Episode|None:
        """
        Get episode in specified branch
        if no episodes in branch then branch parent episode is returned
        if no parent or branch not exists then None is returned
        """
        if branch_name not in self.branches.data:
            if not_exist_ok is True:
                return None
            else:
                raise ValueError(f"Branch '{branch_name}' is not in a document!")

        branch = self.branches.data[branch_name]
        if len(branch.arc.episodes) == 0:
            if branch.parent is not None:
                return branch.parent
            else:
                return None

        return branch.arc.episodes[-1]

    def ensure_branch(self, branch_name:str, parent:Episode):
        """
        Make sure branch exists. If not create one
        """
        if branch_name in self.branches.data:
            return True
        self.branches.data[branch_name] = Story(Arc([]), parent)