# Copyright (c) Microsoft. All rights reserved.

"""This sample code demonstrates how to use an existing APO algorithm to tune the prompts."""

import logging
import os
from typing import Tuple, cast

from openai import AsyncOpenAI
from room_selector import RoomSelectionTask, load_room_tasks, prompt_template_baseline, room_selector

from agentlightning import Trainer, setup_logging
from agentlightning.adapter import TraceToMessages
from agentlightning.algorithm.apo import APO
from agentlightning.types import Dataset
from agentlightning.tracer.agentops import AgentOpsTracer


import agentops



def load_train_val_dataset() -> Tuple[Dataset[RoomSelectionTask], Dataset[RoomSelectionTask]]:
    dataset_full = load_room_tasks()
    train_split = len(dataset_full) // 2
    dataset_train = [dataset_full[i] for i in range(train_split)]
    dataset_val = [dataset_full[i] for i in range(train_split, len(dataset_full))]
    return cast(Dataset[RoomSelectionTask], dataset_train), cast(Dataset[RoomSelectionTask], dataset_val)


def setup_apo_logger(file_path: str = "apo.log") -> None:
    """Dump a copy of all the logs produced by APO algorithm to a file."""

    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] (Process-%(process)d %(name)s)   %(message)s")
    file_handler.setFormatter(formatter)
    logging.getLogger("agentlightning.algorithm.apo").addHandler(file_handler)


def main() -> None:
    setup_logging()
    setup_apo_logger()

    # init agentops
    agentops.init(
        api_key=os.environ["AGENTOPS_API_KEY"],
        tags=["room_selector", "apo", "dev"],  # 可选：添加标签
    )

    #创建禁用自动管理的 tracer
    tracer = AgentOpsTracer(
        agentops_managed=False,  # 关键：禁用自动 dummy key
        instrument_managed=True,
    )

    openai_client = AsyncOpenAI()

    algo = APO[RoomSelectionTask](
        openai_client,
        gradient_model="deepseek-chat",
        apply_edit_model="deepseek-chat",
        val_batch_size=10,
        gradient_batch_size=4,
        beam_width=2,
        branch_factor=2,
        beam_rounds=2,
        _poml_trace=True,
    )
    trainer = Trainer(
        algorithm=algo,
        # Use single runner with shared memory strategy for MacOS compatibility
        n_runners=1,
        strategy="shm",  # Use threads instead of processes
        # APO algorithm needs a baseline
        # Set it either here or in the algo
        initial_resources={
            # The resource key can be arbitrary
            "prompt_template": prompt_template_baseline()
        },
        # APO algorithm needs an adapter to process the traces produced by rollouts
        # Use this adapter to convert spans to messages
        adapter=TraceToMessages(),
        tracer=tracer,
    )
    dataset_train, dataset_val = load_train_val_dataset()
    trainer.fit(agent=room_selector, train_dataset=dataset_train, val_dataset=dataset_val)


if __name__ == "__main__":
    main()
