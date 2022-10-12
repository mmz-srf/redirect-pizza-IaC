import os
import requests
import yaml
import time

class Cli(object):
    commands: list = [
        'push',
        'pull',
    ]
    pizzaHeaders: dict = {}

    def __init__(self):
        pizzaToken = os.environ.get('PIZZA_TOKEN')
        if pizzaToken is None:
            raise Exception('ENV var PIZZA_TOKEN is not set')
            
        self.pizzaHeaders = {
            'Authorization': 'Bearer {}'.format(pizzaToken)
        }

    def getCommands(self) -> list:
        return self.commands

    def dispatch(self, arguments: dict = {}) -> bool:
        
        self.force = arguments.force
        self.dryrun = arguments.dryrun

        match arguments.command:
            case 'push':
                self.push()
            case 'pull':
                self.pull()
            case _:
                raise Exception('Command "{}" not implemented'.format(arguments.command))

        return False

    def pull(self):
        dataApi = self.getApiData()
        dataLocal = self.getLocalData()

        if dataApi == dataLocal:
            print('No changes to pull')
            return
        else:
            self.writeToDisk(dataApi)

    def push(self):
        dataApi = self.getApiData()
        dataLocal = self.getLocalData()

        if dataApi == dataLocal:
            print('No changes to push')
            return
        else:
            print('changes to push')

            updateID = False
            # compare local to remote for updates and creates
            for redirect in dataLocal:
                if redirect.get('id') is None:
                    self.createRedirect(redirect)
                    updateID = True
                else:
                    redirectApi = self.findRedirect(dataApi, redirect.get('id'))
                    if redirectApi != redirect:
                        self.updateRedirect(redirect)
            
            # compare remote to local for deletes
            for redirect in dataApi:
                redirectLocal = self.findRedirect(dataLocal, redirect.get('id'))
                if redirectLocal == {}:
                    self.deleteRedirect(redirect)

            if updateID:
                # requires a second request to get the ID
                time.sleep(1)
                dataApi = self.getApiData()
                self.writeToDisk(dataApi)

    def findRedirect(self, data: list, id: str) -> dict:
        for redirect in data:
            if redirect.get('id') == id:
                return redirect
        return {}

    def ask(self, question: str = '') -> bool:
        if self.force:
            print(question+' [Y/n] y')
            return True
        answer = input(question+' [Y/n] ')
        if answer == 'y' or answer == 'Y' or answer == '':
            return True
        else:
            return False

    def updateRedirect(self, changedItem: dict):
        if self.ask(f"update redirect {changedItem.get('destination')} {changedItem.get('id')}?"):
            if not self.dryrun:
                requests.put('https://redirect.pizza/api/v1/redirects/{}'.format(changedItem.get('id')), headers=self.pizzaHeaders, json=changedItem)
                print("done")
            else:
                print("dryrun")

    def deleteRedirect(self, changedItem: dict):
        if self.ask(f"delete redirect {changedItem.get('destination')} {changedItem.get('id')}?"):
            if not self.dryrun:
                requests.delete('https://redirect.pizza/api/v1/redirects/{}'.format(changedItem.get('id')), headers=self.pizzaHeaders)
                print("done")
            else:
                print("dryrun")
                
    def createRedirect(self, changedItem: dict):
        if self.ask(f"create redirect {changedItem.get('destination')}?"):
            if not self.dryrun:
                requests.post('https://redirect.pizza/api/v1/redirects', headers=self.pizzaHeaders, json=changedItem)
                print("done")
            else:
                print("dryrun")

    def getApiData(self):
        redirects = requests.get('https://redirect.pizza/api/v1/redirects?per_page=500', headers=self.pizzaHeaders)
        data = redirects.json().get('data')

        # remove dynamic data from the response
        for destination in data:
            del destination['updated_at']
            del destination['created_at']
            del destination['domains']
            sources = []
            for source in destination['sources']:
                sources.append(source['url'])

            destination['sources'] = sources

        return data

    def getLocalData(self):
        f = open("redirects.yaml", "r")
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data

    def writeToDisk(self, data: dict):

        if self.ask("Update local file?"):
            if not self.dryrun:
                dataYaml = yaml.dump(data)
                f = open("redirects.yaml", "w")
                f.write(dataYaml)
                f.close()
                print('changes written to disk')
            else:
                print('changes written to disk: dryrun')
        else :
            print('no changes written to disk')