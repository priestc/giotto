from giotto.programs import Program, Manifest
from giotto.programs.shell import shell
from giotto.programs.tables import make_tables, blast_tables
from giotto.views import BasicView

management_manifest = Manifest({
    'make_tables': Program(
        name="Make Tables",
        controllers=['cmd'],
        model=[make_tables],
        view=BasicView()
    ),
    'blast_tables': Program(
        name="Blast Tables",
        controllers=['cmd'],
        model=[blast_tables],
        view=BasicView(),
    ),
    'shell': Program(
        name="Giotto Shell",
        controllers=['cmd'],
        model=[shell],
        view=BasicView(),
    ),
})