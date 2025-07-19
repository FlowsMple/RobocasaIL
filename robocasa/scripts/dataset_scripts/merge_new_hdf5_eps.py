import os
import argparse
import shutil
import robocasa

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_dir",
        type=str,
        help="base directory of episodes",
        default=os.path.join(os.path.dirname(robocasa.__path__[0]), "datasets/v0.5"),
    )
    parser.add_argument(
        "--from_dir",
        type=str,
        help="directory of new episodes to import",
        required=True,
    )
    args = parser.parse_args()

    base_dir = args.base_dir
    from_dir = args.from_dir

    # level 1: train / test
    # level 2: atomic / composite
    # level 3: task name
    # level 4: date tag

    for split in os.listdir(from_dir):
        from_dir_l1 = os.path.join(from_dir, split)
        if not os.path.isdir(from_dir_l1):
            continue
        for task_type in os.listdir(from_dir_l1):
            from_dir_l2 = os.path.join(from_dir, split, task_type)
            if not os.path.isdir(from_dir_l2):
                continue
            for task_name in os.listdir(from_dir_l2):

                from_dir_l3 = os.path.join(from_dir, split, task_type, task_name)
                if not os.path.isdir(from_dir_l3):
                    continue
                for date_tag in os.listdir(from_dir_l3):
                    from_dir_l4 = os.path.join(
                        from_dir, split, task_type, task_name, date_tag
                    )
                    if not os.path.isdir(from_dir_l4):
                        continue

                    base_dir_l3 = os.path.join(base_dir, split, task_type, task_name)
                    if not os.path.exists(base_dir_l3):
                        copy_from = from_dir_l4
                        copy_to = os.path.join(base_dir_l3, date_tag)
                        print("DOES NOT EXIST!")
                        print("COPY FROM:", copy_from)
                        print("COPY TO:", copy_to)
                        shutil.copytree(copy_from, copy_to)
                        print()
                    else:
                        copy_from = from_dir_l4
                        copy_to = None
                        for base_date_tag in os.listdir(base_dir_l3):
                            copy_to = os.path.join(base_dir_l3, base_date_tag)
                            if os.path.isdir(copy_to):
                                break
                        print(
                            "EXISTS!",
                        )
                        print("COPY FROM:", copy_from)
                        print("COPY TO:", copy_to)
                        shutil.copytree(copy_from, copy_to, dirs_exist_ok=True)
                        print()
