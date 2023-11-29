import requests
import os
import lib.koshi8bit.easy_living as el
import random


def git_clone(url: str):
    cmd = f"git clone {url}"
    os.system(cmd)
    return True


def parce_response(response):
    json = response.json()
    print(f"Repos count: {len(json)}")
    clone_urls = list(map(lambda x: (x["clone_url"], ), json))
    # print(len(clone_urls), clone_urls)
    results = el.Utils.start_thread_pool(git_clone, clone_urls)
    # print(len(results), list(map(lambda x: str(x), results)))

    failed = list(filter(lambda x: x.exception is not None, results))
    if failed:
        for task in failed:
            print(str(task))
            # print(len(failed), list(map(lambda x: str(x), failed)))
        raise ConnectionError(f"Some repo download error (count = {len(failed)})")

    print("Download ok!")


def main():
    # user_name = input("Enter github user name\n")
    user_name = "flipperdevices"
    if not user_name:
        raise ValueError("Username should be filled")
    root_folder = input("Enter root folder to download\n")
    default_root_folder = "./download"
    if not root_folder:
        root_folder = default_root_folder
        print(f"default path was set: {os.path.abspath(default_root_folder)}")

    root_folder = os.path.join(root_folder, user_name)
    el.Utils.dir_create(root_folder)
    os.chdir(root_folder)

    api_url = f"https://api.github.com/users/{user_name}/repos?per_page=1000"
    try:
        print("Trying to request..")
        response = requests.get(api_url)
        parce_response(response)
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()
