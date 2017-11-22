#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from frontera import FrontierManager, Settings, FrontierTester

from frontera.utils import graphs

from frontera.utils.tester import DownloaderSimulator

SITE_LIST = [
    [('https://www.alibaba.com', [])],
    [('https://www.baidu.com',[])],
]

def test_backend(backend):
    # Graph
    graph = graphs.Manager()
    # graph.add_site_list(graphs.data.SITE_LIST_02)
    graph.add_site_list(SITE_LIST)

    # Frontier
    settings = Settings()
    settings.BACKEND = backend
    settings.TEST_MODE = True
    frontier = FrontierManager.from_settings(settings)

    # Tester
    tester = FrontierTester(frontier, graph, DownloaderSimulator(10))
    tester.run(add_all_pages=True)

    # Show crawling sequence
    print('-'*40)
    print(frontier.backend.name)
    print('-'*40)
    for page in tester.sequence[0][0]:
        print(page.url)

if __name__ == '__main__':
    import sys
    print(sys.path)
    test_backend('frontier.backend.CustomBackend')
    # test_backend('frontera.contrib.backends.memory.FIFO')
