# Copyright 2019 CEA
# Author: Yann Leprince <yann.leprince@cea.fr>
#
# This file is part of hbp-spatial-backend.
#
# hbp-spatial-backend is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# hbp-spatial-backend is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with hbp-spatial-backend. If not, see <https://www.gnu.org/licenses/>.

import collections
import logging

logger = logging.getLogger(__name__)


class TransformGraph:
    def __init__(self):
        self.links = {}

    @classmethod
    def from_yaml(cls, yaml_stream):
        import yaml
        links = yaml.safe_load(yaml_stream)
        if not isinstance(links, dict):
            raise ValueError('Malformed TransformGraph YAML file')
        # Ensure that every space that is listed as a target also appears as a
        # source
        sources_to_add = []
        for source, targets in links.items():
            for target in targets:
                if target not in links:
                    logger.warning('Missing top-level entry for space %r in '
                                   'the YAML stream (%s)',
                                   target,
                                   getattr(yaml_stream, 'name',
                                           '<unnamed stream>'))
                    sources_to_add.append(target)
        for space in sources_to_add:
            links.setdefault(space, {})
        tg = cls()
        tg.links = links
        return tg

    def add_space(self, name):
        name = str(name)
        if name in self.links:
            raise ValueError('there is already a space named {0}'.format(name))
        self.links[name] = {}

    def add_link(self, from_space, to_space, transform_file):
        if to_space in self.links[from_space]:
            raise ValueError('{0} already has a link to {1}'.format(from_space,
                                                                    to_space))
        self.links[from_space][to_space] = transform_file

    def remove_link(self, from_space, to_space):
        del self.links[from_space][to_space]

    def get_transform_chain(self, from_space, to_space):
        # Trigger KeyError if the source or target space does not exist
        self.links[from_space]
        self.links[to_space]

        to_visit = collections.deque([from_space])
        visited = {from_space}
        back_pointers = {from_space: (None, None)}
        # Breadth-first search on the spaces to find the shortest path
        while True:
            try:
                space = to_visit.popleft()
            except IndexError:
                return None

            # TODO detect ambiguities (multiple same-length chains)
            if space == to_space:
                chain = []
                while back_pointers[space][0] is not None:
                    space, transform = back_pointers[space]
                    chain.append(transform)
                chain.reverse()
                return chain

            for target_space, transform in self.links[space].items():
                if target_space not in visited:
                    visited.add(target_space)
                    to_visit.append(target_space)
                    back_pointers[target_space] = (space, transform)

    def export_graphviz(self, f):
        import string

        def filter_name(name):
            for c in name:
                if c in string.digits + string.ascii_letters + '_':
                    yield c
                else:
                    yield '_'

        name_transforms = {name: ''.join(filter_name(name))
                           for name in self.links}
        target_names = set(name_transforms.values())
        # check non-ambiguity of filtered names
        assert len(target_names) == len(self.links)
        f.write('digraph transforms {\n')
        for name, targets in self.links.items():
            for target_name in targets:
                f.write('\t{0} -> {1};\n'.format(
                    name_transforms[name],
                    name_transforms[target_name]
                ))
        f.write('}\n')
