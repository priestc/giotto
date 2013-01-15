from giotto.programs import GiottoProgram, ProgramManifest
from giotto.programs.shell import shell
from giotto.programs.tables import make_tables, blast_tables
from giotto.views import BasicView

management_manifest = ProgramManifest({
    'make_tables': GiottoProgram(
        controllers=['cmd'],
        model=[make_tables],
        view=BasicView
    ),
    'blast_tables': GiottoProgram(
        controllers=['cmd'],
        model=[blast_tables],
        view=BasicView,
    ),
    'shell': GiottoProgram(
        controllers=['cmd'],
        model=[shell],
        view=BasicView,
    ),
})