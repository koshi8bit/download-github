import requests
import os
import lib.koshi8bit.easy_living as el
import subprocess
import validators


def git_clone(url: str):
    tmp = url.split("/")
    user = tmp[-2]
    repo = tmp[-1]
    if el.Utils.dir_exist(repo):
        raise ValueError("Repo is already exists")
    subprocess.run(["git", "clone", url], check=True)
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
    user_name_or_url = input("Enter github user name or repo URL\n")
    if not user_name_or_url:
        raise ValueError("Username or repo URL should be filled")

    default_root_folder = r"G:\koshi8bit\prog\flipper"
    root_folder = input(f"Enter root folder to download (default: {default_root_folder})\n")
    # default_root_folder = "./download"
    if not root_folder:
        root_folder = default_root_folder
        print(f"default path was set: {os.path.abspath(default_root_folder)}")

    is_url = validators.url(user_name_or_url)
    if is_url:
        try:
            user_name = user_name_or_url.split("/")[-2]
        except Exception as e:
            raise ValueError(f"Invalid URL ({str(e)})")
        print("URL mode (one repo download)")
    else:
        user_name = user_name_or_url
        print("USER mode (all users repo download)")

    root_folder = os.path.join(root_folder, user_name)
    el.Utils.dir_create(root_folder)
    os.chdir(root_folder)

    if is_url:
        # subprocess.run(["git", "clone", user_name_or_url], check=True)
        git_clone(user_name_or_url)
    else:
        api_url = f"https://api.github.com/users/{user_name}/repos?per_page=1000"
        print("Trying to request..")
        response = requests.get(api_url)
        parce_response(response)


if __name__ == '__main__':
    main()
