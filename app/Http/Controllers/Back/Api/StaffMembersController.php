
<?php namespace App\Http\Controllers\Back\Api;

use App\Http\Controllers\Back\Controller;
use App\Http\Resources\StaffMemberResource;
use App\Models\Meta;
use App\Models\StaffMember;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;
use Illuminate\Http\Response;

class StaffMembersController extends Controller
{
    /**
     * Display a paginated list of staff members.
     *
     * @param Request $request
     * @return ResourceCollection
     */
    public function index(Request $request)
    {
        /** @var Collection $staffMembers */
        $staffMembers = StaffMember::query()
            ->withDrafts()
            ->with(['media', 'meta'])
            ->ordered()
            ->applyFilters($request->all())
            ->paginate();

        return StaffMemberResource::collection($staffMembers);
    }

    /**
     * Create a new staff member.
     *
     * @param Request $request
     * @return StaffMemberResource
     */
    public function store(Request $request)
    {
        $this->validateStaffMember($request);

        $staffMember = $this->populateStaffMember(new StaffMember(), $request);

        $staffMember->save();

        $this->attachMedia($staffMember, $request);

        // Save meta...
        $staffMember->saveMeta($request->input('meta', []));

        // Schedule the staff member...
        $staffMember->publishAt(Carbon::parse($request->input('published_at')));

        return new StaffMemberResource($staffMember);
    }

    /**
     * Display the specified staff member.
     *
     * @param int $id
     * @return StaffMemberResource
     */
    public function show($id)
    {
        /** @var StaffMember $StaffMember */
        $staffMember = StaffMember::query()
            ->withDrafts()
            ->with(['media', 'meta'])
            ->findOrFail($id);

        return new StaffMemberResource($staffMember);
    }

    /**
     * Update the specified staff member.
     *
     * @param Request $request
     * @param int $id
     * @return StaffMemberResource
     */
    public function update(Request $request, $id)
    {
        /** @var staffMember $StaffMember */
        $staffMember = StaffMember::query()
            ->withDrafts()

            ->findOrFail($id);

        $this->validateStaffMember($request);

        $staffMember = $this->populateStaffMember($staffMember, $request);

        $staffMember->save();

        $this->detatchMedia();

        $this->attachMedia($staffMember, $request);

        // Save meta...
        $staffMember->saveMeta($request->input('meta', []));

        // Schedule the staff member...
        $staffMember->publishAt(Carbon::parse($request->input('published_at')));

        return new StaffMemberResource($staffMember);
    }

    /**
     * Move the specified staff member.
     *
     * @param Request $request
     * @param int $id
     * @return Response
     */
    public function move(Request $request, $id)
    {
        $staffMember = StaffMember::query()
            ->withDrafts()
            ->findOrFail($id);

        $request->validate([
            'direction' => 'required|in:up,down',
        ]);

        $request->input('direction') === 'down'
            ? $staffMember->moveOrderDown()
            : $staffMember->moveOrderUp();

        return response()->noContent();
    }

    /**
     * Delete the specified staff member.
     *
     * @param int $id
     * @return Response
     */
    public function destroy($id)
    {
        staffMember::query()
            ->withDrafts()
            ->findOrFail($id)
            ->delete();

        return response()->noContent();
    }

    /**
     * Validate the request.
     *
     * @param Request $request
     * @return void*
     */
    protected function validateStaffMember(Request $request)
    {
        $request->validate(
            array_merge(
                [
                    'name' => 'required|string:max:255',
                    'slug' => 'nullable|string:max:255',
                    'image' => 'required|exists:media,id',
                    'published_at' => 'nullable|required|date',
                ],
                Meta::rules()
            )
        );
    }

    protected function populateStaffMember(
        StaffMember $staffMember,
        Request $request
    ) {
        return tap($staffMember, function (StaffMember $staffMember) use (
            $request
        ) {
            $staffMember->name = $request->input('name');
            $staffMember->slug = $request->input('slug');
            $staffMember->description = $request->input('description');
        });
    }

    protected function attachMedia(StaffMember $staffMember, Request $request)
    {
        $staffMember->attachMedia($request->input('image_id'), 'image');
    }
}
