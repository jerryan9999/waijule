# -*- utf-8 -*-

from selenium import webdriver
import json
import re
import csv


#config web browser
driver=webdriver.PhantomJS(executable_path='./phantomjs/bin/phantomjs')
driver.set_window_size(1024, 768)


def fill_up_urls(cityarea,page):
  url = "http://www.waijule.com/agents?cityArea={}&".format(cityarea)+"page="+str(page)
  driver.get(url)
  driver.save_screenshot('screen_{}.png'.format(page))
  anchor_list = driver.find_elements_by_xpath('//*[@id="agent-list"]/agent-list-item/md-list-item/div[1]/div[2]/agent-basic-info/div/div[1]/a')
  for anchor in anchor_list:
    urls.append(anchor.get_attribute('href'))

def process_contact(item):
  return item

def get_agent_info(agent_url):
  #url = "http://www.waijule.com/agents/cl-tang.html?fromUrl=%252Fagents%253FcityArea%253DSEA%2526page%253D1"
  #url = "http://www.waijule.com/agents/wei-younts.html?fromUrl=%252Fagents%253FcityArea%253DSEA%2526page%253D1"
  driver.get(agent_url)
  item = {}
  try:
    item['name'] = driver.find_element_by_css_selector('.wjl-text-24px').text
  except:
    print('Error for agent_url,try again:{}'.format(agent_url))
    try:
      driver.get(agent_url)
      item['name'] = driver.find_element_by_css_selector('.wjl-text-24px').text
    except:
      print("Error two times!")
      return 
  item['url'] = agent_url

  # info
  item['company'] = driver.find_element_by_xpath('//*[@id="view-content"]/div[2]/div/div/div/div[1]/agent-detail-header/div/div[1]/div[2]/div[2]/div[2]').text
  item['personal_website'] = driver.find_element_by_xpath('//*[@id="introduction-tab"]/agent-detail-introduction/div/div[1]/div[2]/div[2]/div[1]').text
  item['addr'] = driver.find_element_by_xpath('//*[@id="introduction-tab"]/agent-detail-introduction/div/div[1]/div[2]/div[2]/div[2]').text

  # comment num.
  num = re.search(r'\((.+)\)条评论',driver.page_source)
  if num:
    item['comment_num'] = num.group(1)

  # three important records: experiences,transactions,visitors
  response = driver.page_source
  tmp_list_num = [e.text for e in driver.find_elements_by_css_selector('.wjl-text-18px')]
  tmp_name_list = []
  if response.find('从业经验</div>') != -1:
    tmp_name_list.append('experiences')
  if response.find('近期成交</div>') !=-1:
    tmp_name_list.append('transactions')
  if response.find('近期访客</div>') !=-1:
    tmp_name_list.append('visitors')
  # compare len of two list
  if len(tmp_name_list)==len(tmp_list_num):
    #print("Right match!")
    for index,name in enumerate(tmp_name_list):
      item[name] = tmp_list_num[index]
  else:
    print("False match")
    raise

  # description 
  item['description'] = driver.find_element_by_xpath('//*[@id="introduction-tab"]/agent-detail-introduction/div/div[2]').text

  item = process_contact(item)

  return item


if __name__ == '__main__':
  
  # agents' urls
  urls = []
  cites = {    #'seattle':['SEA',28],         # cityArea max page
               'boston':['BOS',15],
               'dallas':['DAL',18],
               'houston':['IAH',33],
               'losangeles':['LAX',146],
               'miami':['MIA',14],
               'nyc':['JFK',2],
          }
  # prepare agents' url list
  for city,value in cites.items():
    if city != 'losangeles':
      for page in range(1,value[1]):
        if page != 0:
          fill_up_urls(cityarea=value[0],page=str(page))
    print("Total agents in {} # equals to {}".format(city,len(urls)))

    # prepare item list
    items = []

    for index,url in enumerate(urls):
      #if index<1000:
      try:
        item = get_agent_info(url)
      except:
        item = None
        print("Problem for {}".format(url))
      if item:
        print("Finishing #{} for {}".format(index+1,item['name']))
        items.append(item)

    # writing to file
    with open("items_{}.csv".format(city),'w') as csvfile:
      fieldnames = ['name','url','company','personal_website','addr','experiences','transactions','visitors','comment_num','description']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      for item in items:
        writer.writerow(item)




