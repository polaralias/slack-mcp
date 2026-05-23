from __future__ import annotations

import unittest

from tests.harness.runtime import HarnessPrerequisiteError, HarnessRuntime


class LiveHarnessTestCase(unittest.IsolatedAsyncioTestCase):
    runtime: HarnessRuntime

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.runtime = HarnessRuntime().start()
        except HarnessPrerequisiteError as exc:
            raise unittest.SkipTest(str(exc)) from exc

    @classmethod
    def tearDownClass(cls) -> None:
        cls.runtime.stop()
