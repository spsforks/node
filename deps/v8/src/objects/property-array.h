// Copyright 2018 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef V8_OBJECTS_PROPERTY_ARRAY_H_
#define V8_OBJECTS_PROPERTY_ARRAY_H_

#include "src/objects/heap-object.h"

// Has to be the last include (doesn't have include guards):
#include "src/objects/object-macros.h"

namespace v8 {
namespace internal {

#include "torque-generated/src/objects/property-array-tq.inc"

class PropertyArray
    : public TorqueGeneratedPropertyArray<PropertyArray, HeapObject> {
 public:
  // [length]: length of the array.
  inline int length() const;
  inline int length(AcquireLoadTag) const;

  // This is only used on a newly allocated PropertyArray which
  // doesn't have an existing hash.
  inline void initialize_length(int length);

  inline void SetHash(int hash);
  inline int Hash() const;

  inline Object get(int index) const;
  inline Object get(PtrComprCageBase cage_base, int index) const;

  inline void set(int index, Object value);
  // Setter with explicit barrier mode.
  inline void set(int index, Object value, WriteBarrierMode mode);

  // Signature must be in sync with FixedArray::CopyElements().
  inline void CopyElements(Isolate* isolate, int dst_index, PropertyArray src,
                           int src_index, int len, WriteBarrierMode mode);

  // Gives access to raw memory which stores the array's data.
  inline ObjectSlot data_start();

  // Garbage collection support.
  static constexpr int SizeFor(int length) {
    return kHeaderSize + length * kTaggedSize;
  }
  static constexpr int OffsetOfElementAt(int index) { return SizeFor(index); }

  DECL_PRINTER(PropertyArray)
  DECL_VERIFIER(PropertyArray)

  // Garbage collection support.
  using BodyDescriptor = FlexibleBodyDescriptor<kHeaderSize>;

  static const int kLengthFieldSize = 10;
  using LengthField = base::BitField<int, 0, kLengthFieldSize>;
  static const int kMaxLength = LengthField::kMax;
  using HashField = base::BitField<int, kLengthFieldSize,
                                   kSmiValueSize - kLengthFieldSize - 1>;

  static const int kNoHashSentinel = 0;

 private:
  DECL_INT_ACCESSORS(length_and_hash)

  DECL_RELEASE_ACQUIRE_INT_ACCESSORS(length_and_hash)

  TQ_OBJECT_CONSTRUCTORS(PropertyArray)
};

}  // namespace internal
}  // namespace v8

#include "src/objects/object-macros-undef.h"

#endif  // V8_OBJECTS_PROPERTY_ARRAY_H_
