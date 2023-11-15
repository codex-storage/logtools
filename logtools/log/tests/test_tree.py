from logtools.log.utils import tree


def test_should_allow_nodes_to_be_added():
    a_tree = tree()
    a_tree['a']['b']['c'] = 'd'
    a_tree['a']['b']['d'] = 'e'

    assert a_tree == {
        'a': {
            'b': {
                'c': 'd',
                'd': 'e'
            }
        }
    }
