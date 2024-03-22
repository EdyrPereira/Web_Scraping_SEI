
from re import findall
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

class Bot():  

  def __init__(self):
    '''Inicia o navegador no método construtor '''
    try:
      print('Atualizando drivers...')
      self.serv = Service(ChromeDriverManager().install())
      options = Options()
      #options.add_argument('--headless')
      options.add_argument('--disable-extensions')
      self.nav = webdriver.Chrome(service = self.serv, options = options)
      self.nav.maximize_window()
      print('Drivers atualizados.')
    except: 
      print('Erro ao atualizar os drivers.')

  def login(self, usr, pwd):
    '''Acessa o site, recebe as credenciais e faz login.'''
    print('Fazendo Login...')
    self.nav.get('https://sei.ma.gov.br')
    sleep(0.5)

    self.nav.find_element(By.XPATH, '//*[@id="txtUsuario"]').send_keys(usr)
    self.nav.find_element(By.XPATH, '//*[@id="pwdSenha"]').send_keys(pwd)  
    self.nav.find_element(By.XPATH, '//*[@id="selOrgao"]').send_keys('SES')
    self.nav.find_element(By.XPATH, '//*[@id="Acessar"]').click()
    sleep(0.5)

    if self.nav.find_element(By.ID, "lnkUsuarioSistema").get_attribute("title") != '':
      print('Login feito com sucesso.')
    else: 
      print('Erro ao fazer login.')

  def buscar(self, proc):
    '''Retorna a localização de um processo''' 
    try:
      print(f'Estou buscando o processo {proc}')
      self.nav.find_element(By.XPATH, '//*[@id="txtPesquisaRapida"]').send_keys(proc, Keys.RETURN)
      sleep(1)

      # Muda de iframe
      iframe = self.nav.find_element(By.XPATH, "//iframe[@id='ifrArvore']")
      self.nav.switch_to.frame(iframe)
      sleep(0.5)
      self.nav.find_element(By.XPATH, '//*[@id="divConsultarAndamento"]/a').click() 
      # Retorna ao default
      self.nav.switch_to.default_content()
      sleep(0.5) 
        
      # Muda de frame
      iframe = self.nav.find_element(By.XPATH, "//iframe[@id='ifrVisualizacao']")
      self.nav.switch_to.frame(iframe)
      sleep(0.5) 
      und = self.nav.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[2]/a').get_attribute('title')
      dt = self.nav.find_element(By.XPATH, '//*[@id="tblHistorico"]/tbody/tr[2]/td[1]').text
      loc = (f'{und} - {dt}')  
      # Retorna ao default
      self.nav.switch_to.default_content()
      sleep(0.5) 
      
      # Adciona os dados coletados à lista
      return loc

    except:
      return 'Erro ao buscar o processo'

  def logout(self):
    '''Sai do sistema e encerra o navegador.'''
    print('Fazendo logout...')
    self.nav.find_element(By.XPATH, '//*[@id="lnkInfraSairSistema"]').click()
    sleep(1)
    self.nav.quit()

  def pesquisa(self, proc):
    '''pesquisa obsercações no processo'''
    print(f'Estou buscando o processo {proc}')
    #muda de iframe
    self.nav.find_element(By.XPATH, '//*[@id="txtPesquisaRapida"]').send_keys(proc, Keys.RETURN)
    sleep(1)
    iframearv = self.nav.find_element(By.XPATH, "//iframe[@id='ifrArvore']")
    self.nav.switch_to.frame(iframearv)
    html = self.nav.page_source    
    sleep(0.5)
    
    #obtem os códigos para cada relatório criado localmente no sei
    cod_el = findall(r'documento_interno\.svg\?11" id="icon(\d+)"', html)
    
    paginas = ''#criando ums str vazia para receber as informações dos despachos
    for cod in cod_el:
      
      self.nav.find_element(By.XPATH, f'//*[@id="span{cod}"]').click()
      
      # Retorna ao default
      self.nav.switch_to.default_content()
      sleep(0.5) 
      #separando html somente no codigo do despacho
 
      # Muda de frame
      iframevis = self.nav.find_element(By.XPATH, "//iframe[@id='ifrVisualizacao']")
      self.nav.switch_to.frame(iframevis)
      sleep(0.5)
      iframehtml = self.nav.find_element(By.XPATH, '//*[@id="ifrArvoreHtml"]')    
      self.nav.switch_to.frame(iframehtml)
      sleep(0.5)

      pagina = self.nav.find_element(By.XPATH, '/html/body')

      pagina = pagina.text#self.nav.page_source
      
      paginas = paginas + pagina + '\n'

      # Retorna ao default
      self.nav.switch_to.default_content()
      sleep(0.5)

      #mudando para o iframe da árvore
      self.nav.switch_to.frame(iframearv)
      sleep(0.5)
    
    t = open('pagina.txt', 'w', encoding='utf-8')
    t.write(paginas)
    t.close()
    #for cod in cod_el:

      #self.nav.find_element(By.XPATH, f'//*[@id="span{cod}"]').click()
    
    sleep(2)

  def lista_processos(self):
    processos = self.nav.find_element(By.XPATH, '//*[@id="tblProcessosRecebidos"]/tbody').text
    
    try:
      self.nav.find_element(By.XPATH, '//*[@id="lnkRecebidosProximaPaginaSuperior"]').click()
      sleep(0.5)
      processos2 = self.nav.find_element(By.XPATH, '//*[@id="tblProcessosRecebidos"]/tbody').text
      processos = processos + processos2

    except:
      pass
    processos_n = findall(r'\d{4}\.\d{6}\.\d{5}', processos) #agora náo é mais tipo str mas sim uma lista
    
    t = open('processos.txt','w', encoding='utf-8')
    for processo in processos_n:
      t.write(f'{processo}\n')
      t.close
### alteração para testes 
    
x = Bot()
x.login('login', 'pwd')
x.pesquisa('n° processo')
x.lista_processos()
x.logout