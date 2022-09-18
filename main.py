from btree import *


def farm():
    nav_fram = py_trees.composites.Selector(
        children=[
            py_trees.behaviours.CheckBlackboardVariableExists("/move/target"),
            py_trees.composites.Sequence(
                children=[
                    py_trees.behaviours.CheckBlackboardVariableExists("/data/map_pos"),
                    py_trees.behaviours.CheckBlackboardVariableExists("/data/player"),
                    WaitForAnimationEnd(),
                    GetTargetFarm(),
                    TurnToTarget(),
                ],
            ),
        ],
    )
    check_fram = py_trees.decorators.Inverter(
        py_trees.composites.Sequence(
            children=[
                py_trees.composites.Selector(
                    children=[
                        py_trees.behaviours.SuccessEveryN(
                            "Counter", 100
                        ),  # 防止转身被延迟卡顿吃掉以后，一直撞墙
                        AtTarget(50, 1000),
                    ]
                ),
                py_trees.behaviours.UnsetBlackboardVariable("/move/target"),
            ]
        )
    )
    skill_fram = py_trees.composites.Selector(
        children=[
            py_trees.decorators.Inverter(WaitForAnimationEnd()),
            Skill(125.0, 0.5, "5"),
            Skill(91.0, 0.8, "1"),
            Skill(121.0, 0.8, "2"),
            Skill(181.0, 0.8, "3"),
            DoubleJumpSkill(10.0, 1.2, "E"),
            DoubleJumpSkill(61.0, 0.95, "T"),
            DoubleJumpSkill(15.1, 0.95, "R"),
            DoubleJumpSkill(0.0, 0.9, "Q"),
        ]
    )

    farm = py_trees.composites.Sequence(
        children=[
            nav_fram,
            check_fram,
            skill_fram,
        ],
    )
    return farm


def rune():


    root = py_trees.composites.Selector(
        children=[
            py_trees.decorators.Inverter(
                py_trees.behaviours.CheckBlackboardVariableExists("/data/rune_pos")
            ),
        ],
    )
    return root


def main():
    # init data gather
    data_gather = DataGather()

    root = py_trees.composites.Sequence(
        children=[
            data_gather,
            py_trees.composites.Selector(children=[farm()]),
        ],
    )
    root.logger.info(py_trees.display.unicode_tree(root))
    root.logger.info(py_trees.display.unicode_blackboard())

    running = threading.Event()

    def set_event():
        if running.is_set():
            running.clear()
            root.logger.info("STOP!")
        else:
            running.set()
            root.logger.info("RUNNING!")

    keyboard.GlobalHotKey({"SHIFT+G": set_event})
    while True:
        if running.is_set():
            root.tick_once()
        time.sleep(0.005)


if __name__ == "__main__":
    main()
