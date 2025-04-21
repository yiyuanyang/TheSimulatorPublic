import time


def main():
    time.sleep(5)
    with open("../command/command.json", "w") as f:
        f.write(
            '[{"CommandType": "Start", "CommandPriority": "Immediate"}]'
        )
    time.sleep(5)
    with open("../command/command.json", "w") as f:
        f.write(
            '[{"CommandType": "Pause", "CommandPriority": "Immediate"}]'
        )
    time.sleep(10)
    with open("../command/command.json", "w") as f:
        f.write(
            '[{"CommandType": "Start", "CommandPriority": "Immediate"}]'
        )


if __name__ == "__main__":
    main()
