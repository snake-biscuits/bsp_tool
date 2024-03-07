class OrderedSet(list):
    """treat as append-only, popping will break indices"""
    def add(self, value) -> int:
        """returns index of value"""
        if value in self:
            return self.index(value)
        else:
            self.append(value)
            return len(self) - 1
