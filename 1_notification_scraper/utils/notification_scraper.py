import os
import re
from datetime import datetime
from playwright.async_api import async_playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def download_draft(tris_url, tris_id):
    tris_path = tris_id.replace('/', '_')
    dwl_path = '../NOTIFICATIONS/' + tris_path + '/notification/'
    os.makedirs(dwl_path, exist_ok=True)

    tris_selectors = {'draft': "#D-links-container"}
    message_selector = "//div[@class='ecl-col-12 ecl-u-border-all ecl-u-border-color-grey-50']"

    language_map = {'SE': 'SV'}  # Add other mappings if needed
    tris_language = tris_id.split('/')[-1]
    target_language = language_map.get(tris_language, tris_language)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(tris_url)

        for tris_type, selector in tris_selectors.items():
            tris_element = page.locator(selector)
            visible_tris = sum([await handle.is_visible() for handle in await tris_element.element_handles()])
            if visible_tris > 0:
                for lang in [target_language, "EN"]:
                    try:
                        async with page.expect_download() as download_info:
                            await tris_element.get_by_role("link", name=lang).click()
                            download_tris = await download_info.value
                            tris_filename = f'{tris_path}_{tris_type.upper()}_{lang}_{download_tris.suggested_filename}'
                            await download_tris.save_as(dwl_path + tris_filename)
                    except TimeoutError:
                        print(f"Timeout or missing file: {tris_type} in {lang}")
                    except Exception as e:
                        print(f"Error downloading {tris_type} in {lang}: {e}")
        
        # Download message
        try:
            message = await page.locator(message_selector).text_content()
            with open(dwl_path + tris_path + "_message.txt", "w") as text_file:
                text_file.write(message)
        except Exception as e:
            print(f"Error retrieving message content: {e}")

        await browser.close()
    
    return f"Completed draft download for {tris_id}"


async def download_final(tris_url, tris_id):
    tris_path = tris_id.replace('/', '_')
    dwl_path = '../NOTIFICATIONS/' + tris_path + '/notification/'

    os.makedirs(dwl_path, exist_ok=True)

    tris_selectors = {'final': "#F-links-container"}
    language_map = {'SE': 'SV'}  # Add other mappings if needed
    tris_language = tris_id.split('/')[-1]
    target_language = language_map.get(tris_language, tris_language)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(tris_url)

        for tris_type, selector in tris_selectors.items():
            tris_element = page.locator(selector)
            visible_tris = sum([await handle.is_visible() for handle in await tris_element.element_handles()])
            if visible_tris > 0:
                for lang in [target_language, "EN"]:
                    try:
                        async with page.expect_download() as download_info:
                            await tris_element.get_by_role("link", name=lang).click()
                            download_tris = await download_info.value
                            tris_filename = f'{tris_path}_{tris_type.upper()}_{lang}_{download_tris.suggested_filename}'
                            await download_tris.save_as(dwl_path + tris_filename)
                    except TimeoutError:
                        print(f"Timeout or missing file: {tris_type} in {lang}")
                    except Exception as e:
                        print(f"Error downloading {tris_type} in {lang}: {e}")

        await browser.close()
    
    return f"Completed final download for {tris_id}"



async def contrib_page(tris_url, tris_id):
    # Path for saving contributions
    tris_path = tris_id.replace('/', '_')
    contrib_base_path = f'../NOTIFICATIONS/{tris_path}/contributions/'
    os.makedirs(contrib_base_path, exist_ok=True)
    
    # Selectors for locating elements on the page
    selectors = {
        'contrib_tab': "Contribution",
        'contrib': "//div[@class='ecl-accordion__item']",
        'contrib_item': "(//button[@class='ecl-accordion__toggle'])",
        'name_lang': "(//span[@class='ecl-accordion__toggle-title'])",
        'doc_type': "(//div[@class='ecl-file__meta'])",
        'dwl_button': "(//a[@class='ecl-link ecl-link--standalone ecl-link--icon ecl-link--icon-after ecl-file__download'])"
    }

    # Initialize results
    contributions = []
    contrib_id = 0
    no_dwl_av_counter = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(tris_url)
        
        # Open the contributions tab
        await page.get_by_role("tab", name=selectors['contrib_tab']).click()

        # Count the number of contributions
        count_contribs = await page.locator(selectors['contrib']).count()
        print('count_contribs',count_contribs)
        for i in range(count_contribs):
            print('i:',i)
            # Expand each contribution section
            await page.click(f"{selectors['contrib_item']}[{i+1}]")
            
            # Extract contributor name and document language
            contributor = await page.locator(f"{selectors['name_lang']}[{i+1}]").text_content()
            
            doc_lang, contributor, contrib_date = entity_name_cleaner(contributor)
            print('contributor',contributor)
            print('contrib_date:',contrib_date)
            # Extract document type
            try:
                print(i+1-no_dwl_av_counter)
                doc_type = await page.locator(f"{selectors['doc_type']}[{i+1-no_dwl_av_counter}]").text_content()
                print(doc_type)
                doc_type = doc_type_cleaner(doc_type)
            except PlaywrightTimeoutError:
                print(f'timeout: while getting meta info for contribution {i+1}')
                contributions.append({'id': contrib_id, 'contributor': contributor, 'date': contrib_date,'language': doc_lang, 'path': None, 'error': 'timeout_meta_info'})
                contrib_id += 1
                continue
            
            # Check if the download button is visible
            dwl = page.locator(selectors['dwl_button'])
            visible = sum([await handle.is_visible() for handle in await dwl.element_handles()])

            if visible > 0:
                index = i + 1 - no_dwl_av_counter
                download_path = f'{contrib_base_path}{contributor}_{doc_lang}{doc_type}'
                
                try:
                    # Download the file
                    await page_downloader(page, selectors['dwl_button'], index, download_path)
                    contributions.append({'id': contrib_id, 'contributor': contributor, 'date': contrib_date,'language': doc_lang, 'path': download_path, 'error': None})
                except PlaywrightTimeoutError:
                    print(f'timeout: while downloading contribution {i+1}')
                    contributions.append({'id': contrib_id, 'contributor': contributor, 'date': contrib_date,'language': doc_lang, 'path': None, 'error': 'timeout_contribution'})
                    no_dwl_av_counter += 1
            else:
                # If no download available, note it in the results
                contributions.append({'id': contrib_id, 'contributor': contributor, 'date': contrib_date,'language': doc_lang, 'path': None, 'error': 'no_download'})
                no_dwl_av_counter += 1
            
            contrib_id += 1
        
        await browser.close()

    return contributions

def entity_name_cleaner(name):
    # Extract document language code
    doc_lang = name.split(')', 1)[0][1:]

    # Extract contributor name up to the substring " on"
    contib_name_part = name.split(')', 1)[1]
    contib_name = contib_name_part.split(" on")[0].strip()
    contib_name = re.sub(r'[^a-zA-Z0-9]+', '_', contib_name).strip('_').lower()
    
    # Extract and format the date if present
    date_str = contib_name_part.split(" on")[-1].strip()
    try:
        contrib_date = datetime.strptime(date_str, "%d-%m-%Y").date()  # Formats as YYYY-MM-DD
    except ValueError:
        contrib_date = None  # In case there's no valid date
    
    return doc_lang, contib_name, contrib_date

def doc_type_cleaner(doc_type):
    return '.' + doc_type.split('-', 1)[1][:-1].strip().lower()

async def page_downloader(page, selector, index, dwl_results_path):
    async with page.expect_download() as download_info:
        await page.click(f"{selector}[{index}]")
        download = await download_info.value
        await download.save_as(dwl_results_path)
