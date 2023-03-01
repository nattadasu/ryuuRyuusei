#!/usr/bin/env python3

import os

def main():
    # check if the file database/database.csv exists
    if not os.path.exists("database/database.csv"):
        # if not, write new header
        with open("database/database.csv", "w") as f:
            f.write("discordId\tdiscordUsername\tdiscordJoined\tmalUsername\tmalId\tmalJoined\tregisteredAt\tregisteredGuild\tregisteredBy")

if __name__ == "__main__":
    main()
