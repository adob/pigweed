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
#pragma once

#include "pw_allocator/allocator.h"

namespace pw::allocator {

/// Memory allocator that uses `malloc` and `free`.
///
/// TODO: b/301930507 - `aligned_alloc` is not portable. As a result, this
/// allocator has a maximum alignment of `std::align_max_t`.
class LibCAllocator : public Allocator {
 public:
  constexpr LibCAllocator() = default;

 private:
  /// @copydoc Allocator::Allocate
  void* DoAllocate(size_t size, size_t alignment) override;

  /// @copydoc Allocator::Deallocate
  void DoDeallocate(void* ptr, size_t size, size_t alignment) override;

  /// @copydoc Allocator::Resize
  bool DoResize(void* ptr,
                size_t old_size,
                size_t old_alignment,
                size_t new_size) override;

  /// @copydoc Allocator::Reallocate
  void* DoReallocate(void* ptr,
                     size_t old_size,
                     size_t old_alignment,
                     size_t new_size) override;
};

}  // namespace pw::allocator
