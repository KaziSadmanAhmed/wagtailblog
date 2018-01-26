from treebeard.mp_tree import MP_NodeQuerySet, MP_NodeManager


class CommentQuerySet(MP_NodeQuerySet):
    def root_nodes(self):
        return self.filter(depth=1)

    def live(self):
        return self.filter(live=True)


class CommentManager(MP_NodeManager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db).order_by("path")

    def root_nodes(self):
        return self.get_queryset().root_nodes()

    def live(self):
        return self.get_queryset().live()
