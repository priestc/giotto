from giotto.programs import Program, Manifest
from giotto.programs.shell import shell
from giotto.programs.tables import syncdb, blast_tables
from giotto.views import BasicView

management_manifest = Manifest({
    'syncdb': Program(
        name="Make Tables",
        controllers=['cmd'],
        model=[syncdb],
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