// Copyright 2023 The Pigweed Authors
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy of
// the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

#include "pw_async_basic/dispatcher.h"
#include "pw_bloat/bloat_this_binary.h"

int main() {
  pw::bloat::BloatThisBinary();

  pw::async::BasicDispatcher dispatcher;
  pw::async::Task task(
      [](pw::async::Context& /*ctx*/) { printf("hello world\n"); });
  dispatcher.PostTask(task);
  dispatcher.Run();
  return 0;
}