import py_trees


class MoveTo(py_trees.behaviour.Behaviour):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.bb = self.attach_blackboard_client()
    
    def update(self):
        '''
        1\ GET TARGET
        2\ GET POSITION
        3\ GET PATH
        4\ MOVE
        '''
        if not self.bb.exists("/move/target"):
            return py_trees.common.Status.FAILURE
        
        player = self.bb.get("/data/player")
        if player is None:
            return py_trees.common.Status.FAILURE


        # target on which platforms?
